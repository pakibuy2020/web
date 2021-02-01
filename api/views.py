from django.shortcuts import render

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .serializers import CartSerializer, CartItemSerializer,ProductSerializer

from cart.models import *
from product.models import Product

from social_django import models as oauth_models
from django.utils import timezone

from django.db import transaction
from django.core.paginator import Paginator

import requests
import json
from requests.auth import HTTPBasicAuth

# get all items
@api_view(["GET",])
def all_paged_items(request,size,page_number):
    try:
        product_list = Product.objects.all()
        paginator = Paginator(product_list, size)
        page_obj = paginator.get_page(page_number)

        serializer = ProductSerializer(page_obj,many=True)
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response(status=204)

# get all featured items
@api_view(["GET",])
def all_items(request):
    try:
        product = Product.objects.all()
        serializer = ProductSerializer(product,many=True)
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response(status=204)

# get all featured items
@api_view(["GET",])
def featured_items(request):
    try:
        product = Product.objects.all().order_by('?')[:6]
        serializer = ProductSerializer(product,many=True)
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response(status=204)

# get all latest items
@api_view(["GET",])
def latest_items(request):
    try:
        product = Product.objects.all().order_by("-date_created")[:6]
        serializer = ProductSerializer(product,many=True)
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response(status=204)

# get all items in the active cart
@api_view(["GET",])
def cart_items(request, customer_email):
    try:
        cart = Cart.objects.get(customer_email=customer_email, status=1)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    except Cart.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

# get all items in the selected cart
@api_view(["GET",])
def cart_items_selected(request, customer_email,cart_id):
    try:
        cart = Cart.objects.get(id=cart_id,customer_email=customer_email)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    except Cart.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

# get all items in the active cart
@api_view(["GET",])
def cart_items_by_id(request, customer_email,cart_id,size,page_number):
    try:
        cart = Cart.objects.get(id=cart_id,customer_email=customer_email)
        car_items = CartItem.objects.filter(cart=cart)
        paginator = Paginator(car_items, size)
        page_obj = paginator.get_page(page_number)
        serializer = CartItemSerializer(page_obj,many=True)
        return Response(serializer.data)
    except Cart.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

# get all carts from a customer
@api_view(["GET",])
def carts(request,customer_email,size,page_number): 
    try:
        cart_list = Cart.objects.filter(customer_email=customer_email).order_by('-date_created')
        paginator = Paginator(cart_list, size)
        page_obj = paginator.get_page(page_number)
        serializer = CartSerializer(page_obj,many=True)
        return Response(serializer.data)
    except Cart.DoesNotExist:
        return Response(status=204)

@transaction.atomic
# remove item from the active cart
@api_view(["DELETE",])
def remove_item(request, id):
    try:
        item = CartItem.objects.get(id=id)
        item.delete()
        return Response(status=status.HTTP_200_OK)
    except Cart.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


# add item in the cart
# if no cart create a new cart
@transaction.atomic
@api_view(["POST",])
def add_item(request):
    email = request.data.get("customer_email")
    product = request.data.get("product_sku")
    qty = request.data.get("qty")
    try:
        Cart.objects.get(customer_email=email, status=1)
    except Cart.DoesNotExist:
        # create cart
        nCart = Cart(customer_email=email, status=1, date_created=timezone.now())
        nCart.save()
    finally:
        # create item
        try:
            cart = Cart.objects.get(customer_email=email, status=1)
            prod = Product.objects.get(sku=product)
            cItem = CartItem(product=prod, qty=qty, cart=cart)
            cItem.save()
        except Product.DoesNotExist:
            return Response(
                message=({"error": "product not found"}),
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_200_OK)


# update item count
@transaction.atomic
@api_view(["PUT",])
def update_item(request):
    cart_item = request.data.get("cart_item_id")
    qty = request.data.get("qty")

    print(qty)
    try:
        CartItem.objects.filter(id=cart_item).update(qty=qty)
        return Response(status=202)
    except CartItem.DoesNotExist:
        return Response(
            message=({"error": "product not found"}), status=status.HTTP_404_NOT_FOUND
        )


# get single item from the active cart
@api_view(["GET",])
def product_item_cart(request, customer_email, product_sku):
    try:
        count = Product.product_item_cart(product_sku, customer_email)
        serializer = CartItemSerializer(count)
        return Response(serializer.data, status=200)
    except CartItem.DoesNotExist:
        return Response(status=204)

# process payment
@transaction.atomic
@api_view(["POST",])
def payment_cod(request):
    cartid = request.data.get("cart_id")
    amount = request.data.get("amount")
    net = request.data.get("net")

    address = request.data.get("address")
    contact = request.data.get("contact")

    net_int =  net.replace('.', '').replace(',','')

    free = (int(net_int) > 1000)

    try:
        cart = Cart.objects.get(id=cartid)
        payment = Payment(cart=cart,net=net,payment_amount=amount,payment_type=2,paymongo_id=None,free_shipping=free)
        payment.save()

        shipping = Shipping(address=address,contact=str(contact),cart=cart)
        shipping.save()

        Cart.objects.filter(id=cartid).update(status=Cart.STATUS.VERIFICATION)
        return Response(status=201)
    except Cart.DoesNotExist:
        return Response(status=500)

# process payment
@transaction.atomic
@api_view(["POST",])
def payment_gcash(request):
    cartid = request.data.get("cart_id")
    amount = request.data.get("amount")
    net = request.data.get("net")

    address = request.data.get("address")
    contact = request.data.get("contact")

    url = "https://api.paymongo.com/v1/sources"

    amount_int = amount.replace('.', '').replace(',','')
    net_int =  net.replace('.', '').replace(',','')

    print(address)
    print(contact)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic cGtfdGVzdF9ISGhDdDZGRnB6aTNaSFh6cHhwV2RjSEs6",
    }
    payload = {
        "data": {
            "attributes": {
                "amount": int(net_int),
                "redirect": {
                    "success": "https://pakibuy.herokuapp.com/",
                    "failed": "https://pakibuy.herokuapp.com/cart/failed/" + cartid,
                },
                "type": "gcash",
                "currency": "PHP",
            }
        }
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    if response.status_code == 200:
        #     #save payment db
        try:
            cart = Cart.objects.get(id=cartid)
            json_data = response.json()
            paymongo_id = json_data['data']['id']
            
            free = (int(net_int) > int(1000.00))

            payment = Payment(cart=cart,net=net,payment_amount=amount,payment_type=1,paymongo_id=paymongo_id,free_shipping=free)
            payment.save()

            Cart.objects.filter(id=cartid).update(status=2)

            shipping = Shipping(address=address,contact=str(contact),cart=cart)
            shipping.save()

            checkout_url = json_data['data']['attributes']['redirect']['checkout_url']
            return Response({'checkout_url': checkout_url})
        except Cart.DoesNotExist:
            return Response(status=500)
    else:
        print(response.text)
        return Response(status=response.status_code)
    # return Response(status=200)

# # webhook that paymongo will call once gcash has been processed
# @transaction.atomic
# @api_view(["POST",])
# def webhook_payment(request):
#     json_data = json.loads(request.body)
#     paymongo_id = json_data['data']['attributes']['data']['id']
#     status = json_data['data']['attributes']['data']['attributes']['status']

#     print(json_data)
#     try:
#         # update payment status        
#         if status == 'chargeable':
#             Payment.objects.filter(paymongo_id=paymongo_id).update(payment_status=1)
#             # update cart status to shipping (since payment has been processed already via gcash and paymongo)
#             payment = Payment.objects.get(paymongo_id=paymongo_id)
#             cart_id = payment.cart.id
#             Cart.objects.filter(id=cart_id).update(status=3)
#     except Payment.DoesNotExist:
#         Response(status=404) 
#     return Response(status=200) 
