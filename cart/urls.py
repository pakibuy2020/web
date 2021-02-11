from django.conf.urls import url, include
from django.urls import path
from . import views

urlpatterns = [
    url(r'^list/', views.list_cart,name="carts"),
    url(r'^$', views.list_cart,name="carts"),
    
    path('view/<cart_id>',views.view_cart),

    path('print/<cart_id>',views.print_reciept),

    path('checkout/', views.checkout),
    path('failed/<cart_id>',views.failed_cart),

    path('address/<person_email>',views.cart_last_address)
]
