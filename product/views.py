from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Product

@login_required
def list_product(request):
    products = Product.objects.all()
    return render(request,'products.html',{'products':products})

@login_required
def list_product_category(request,category):
    products = Product.objects.filter(category=category)
    return render(request,'products.html',{'products':products})

@login_required
def single_product(request,sku):
    product = Product.objects.get(sku=sku)
    return render(request,'single_product.html',{'product':product}) 
  