from django.db import models
from social_django import models as oauth_models

class Cart(models.Model):
    class STATUS(models.IntegerChoices):
        SHOPPING = 1,
        PAYMENT = 2,
        SHIPPING = 3,
        RECIEVED = 4,
        CANCELLED = 5,
        VERIFICATION = 6

    customer_email = models.CharField(max_length=50)
    description = models.TextField(max_length=30)
    # user =models.ForeignKey(oauth_models.USER_MODEL,on_delete=models.CASCADE)
    status = models.IntegerField(choices=STATUS.choices,default=STATUS.SHOPPING)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)


class CartItem(models.Model):
    qty = models.IntegerField()
    last_modified = models.DateTimeField(auto_now_add=True)
    # products = models.ForeignKey(Product, on_delete=models.CASCADE)
    product = models.ForeignKey('product.Product', on_delete=models.CASCADE,unique=False)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    
    def __str__(self):
        return str(self.id)    

class Payment(models.Model):
    class PAYMENT_TYPE(models.IntegerChoices):
        GCASH = 1,
        COD = 2
    class PAYMENT_STATUS(models.IntegerChoices):
        PAID = 1,
        INPROGRESS = 2,
        EXPIRED = 3,
        CANCELLED = 4    

    paymongo_id = models.CharField(max_length=50,null=True,blank=True)
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE)
    net = models.DecimalField(max_digits=7, decimal_places=2)
    payment_amount = models.DecimalField(max_digits=7, decimal_places=2)
    free_shipping = models.BooleanField(default=False)
    payment_type = models.IntegerField(choices=PAYMENT_TYPE.choices)
    payment_status = models.IntegerField(choices=PAYMENT_STATUS.choices,default=PAYMENT_STATUS.INPROGRESS)
    # address = models.CharField(blank=True,null=True,max_length=80)
    date_created = models.DateTimeField(auto_now_add=True)

class Shipping(models.Model):
    address = models.CharField(max_length=50)
    contact = models.IntegerField()
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE)


# class ReturnCart(models.Model):
#     cart = models.ForeignKey(Cart,on_delete=models.CASCADE)
#     date_created = models.DateTimeField(auto_now_add=True)
    