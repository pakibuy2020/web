from django.conf.urls import include, url
from django.urls import path

from .views import *

urlpatterns = [
#    url(r'^cart/$',cart_items),
    path('cart/<customer_email>',cart_items),
    path('cart/view/<customer_email>/<cart_id>',cart_items_selected),
    path('cart/items/<customer_email>/<cart_id>/<size>/<page_number>',cart_items_by_id),

    path('cart/item/add',add_item),
    path('cart/item/remove/<id>',remove_item),
    path('cart/item/update',update_item),

    path('cart/checkitem/<customer_email>/<product_sku>',product_item_cart),

    path('cart/payment/gcash/',payment_gcash),
    path('cart/payment/cod/',payment_cod),

    # path('cart/payment/webhook',webhook_payment),
    path('cart/list/<customer_email>/<size>/<page_number>',carts),


    # product related api
    path('product/all/<size>/<page_number>',all_paged_items),
    path('product/featured',featured_items),
    path('product/latest',latest_items),
    # path('product/latest',all_items)

    
]

