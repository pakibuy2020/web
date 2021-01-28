from rest_framework import serializers

from cart.models import Cart,CartItem
from product.models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('sku','name','price','cover_photo','description')

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    class Meta:
        model = CartItem
        fields = ('id','qty','last_modified','product',)

class CartSerializer(serializers.ModelSerializer):
    cartitem = CartItemSerializer(source='cartitem_set',many=True)
    class Meta:
        model = Cart
        fields = ['id','customer_email','status','date_created','cartitem']
