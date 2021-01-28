from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from product.models import Product

@login_required
def home(request):
    return render(request,'home.html')
