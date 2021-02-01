from django.db import models
from django.db.models import Sum
# from tinymce.models import HTMLField
from django.core.validators import MinValueValidator
from cart.models import CartItem,Cart

# category
# class Category(models.Model):
#     class ParentCategory(models.IntegerChoices):
#         HOUSEHOLD = 0,
#         PERSONAL_CARE = 1,
#         BABY_CARE = 2,
#         COOKING =3,
#         GOODS = 4,
#         BEVERAGES = 5,
#         SNAKS = 6,
#         FRESH = 7

#     name = models.CharField(max_length=30)
#     parent_category = models.IntegerField(choices=ParentCategory.choices)
#     description = models.TextField()
#     date_created = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.name

#     class Meta:
#         managed = True
#         verbose_name = 'Category'
#         verbose_name_plural = 'Categories'

# supplier
class Supplier(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        verbose_name = 'Supplier'
        verbose_name_plural = 'Suppliers'   

# product
# every product can have multiple categories 
class Product(models.Model):
    class Category(models.IntegerChoices):
        HOUSEHOLD = 0,
        PERSONAL_CARE = 1,
        BABY_CARE = 2,
        COOKING =3,
        GOODS = 4,
        BEVERAGES = 5,
        SNAKS = 6,
        FRESH = 7    
    category = models.IntegerField(choices=Category.choices)
    sku = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=30)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    date_created = models.DateTimeField(auto_now_add=True)
    cover_photo = models.ImageField(upload_to="gallery",blank=True,null=True)
    

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        verbose_name = 'Product'
        verbose_name_plural = 'Products'


    def product_item_cart(sku,customer_email):
        product = Product.objects.get(sku=sku)
        cartItem = CartItem.objects.get(product=product,cart__status=1,cart__customer_email=customer_email)
        return cartItem

    def current_stock(self):
        product = Product.objects.get(sku=self.sku)
        stock = Stock.objects.filter(product=product).aggregate(Sum('stock'))['stock__sum']
        # qty = CartItem.objects.filter(product=product).exclude(cart__status__in=[3,4]).aggregate(Sum('qty'))['qty__sum']
        qtyRecieved = CartItem.objects.filter(product=product,cart__status=4).aggregate(Sum('qty'))['qty__sum']
        qtyShipping = CartItem.objects.filter(product=product,cart__status=3).aggregate(Sum('qty'))['qty__sum']

        qtyTotal = ((0 if qtyRecieved is None else qtyRecieved) + (0 if qtyShipping is None else qtyShipping))
        tempStock = (0 if stock is None else stock)

        # return 0
        return (stock if qtyTotal is None else tempStock - qtyTotal)

# stock detail of each product - keep history
class Stock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier,on_delete=models.CASCADE)
    stock = models.PositiveIntegerField(null=False,validators=[MinValueValidator(0)])
    last_updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        verbose_name = 'Stock'
        verbose_name_plural = 'Stocks'     