from django.conf.urls import url, include
from . import views
from django.urls import path

urlpatterns = [
    # all products
    url(r'^list/', views.list_product,name="products"),

    path('specific/<category>', views.list_product_category,name="products"),

    # single product
    url(r'^(?P<sku>[\w-]+)/$', views.single_product),

    url(r'^$',views.list_product,name="products"),
]
