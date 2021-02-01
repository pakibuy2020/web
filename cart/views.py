from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import *

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .utils import *

@login_required
def list_cart(request):
    return render(request, "items.html",{'is_view':'false'})


@login_required
def checkout(request):
    return render(request, "checkout.html")

@login_required
def view_cart(request,cart_id):
    return render(request, "items.html",{'is_view':'true','cart_id':cart_id})

@login_required
def failed_cart(request,cart_id):
    # since payment failed update the status back to shopping
    Cart.objects.filter(id=cart_id).update(status=1)
    return render(request, "items.html")

# # api to view receipt
@api_view(["GET"],)
def print_reciept(request,cart_id):
    cart = Cart.objects.get(id=cart_id)
    cart_items = CartItem.objects.filter(cart=cart)

    total = 0.00
    net = 0.00
    shipping = 100.00

    for item in cart_items:
        price = item.product.price
        qty = item.qty
        total = total + float(price * qty)

    if total >= 1000:
        shipping = 'Free Shipping'
        net = 'Php ' + str(total)
    else:
        shipping = 'Php ' + str(100.00)
        net = 'Php ' + str(total + float(100.00))


    context = {'cart':cart,'cartItems': cart_items,'total' : 'Php ' + str(total),'net': str(net),'shipping': shipping }
    
    
    pdf = render_to_pdf('reciept.html',context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "Reciept_%s.pdf" %(cart_id)
        content = "inline; filename=%s" %(filename)
        download = request.GET.get("download")
        if download:
            content = "attachment; filename=%s" %(filename)
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Not Found")