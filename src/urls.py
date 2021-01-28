from django.contrib import admin
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from home.views import home

admin.site.site_header = 'PakiBuy Admin Panel'                    # default: "Django Administration"
admin.site.index_title = 'Features menu'                 # default: "Site administration"
admin.site.site_title = 'Admin Panel | Pakibuy'

urlpatterns = [
    url(r"^admin/", admin.site.urls),
    # url(r'^admin/dynamic_raw_id/', include('dynamic_raw_id.urls')),
    # url(r'^tinymce/', include('tinymce.urls')),

    # home app
    url(r"^$", home, name="home"),
    url(r"^home/$", home, name="home"),

    # for social login
    url(r"^login/$", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    url(r"^logout/$", auth_views.LogoutView.as_view(), name="logout"),
    
    url(r"^oauth/", include("social_django.urls", namespace="social")),

    # product app
    url(r"^product/", include("product.urls")),

    # cart page
    url(r"^cart/", include("cart.urls")),

    # api
    # url('',PasabuyAPI.as_view(),name="api")
    url(r'^api/',include("api.urls"))

]+ static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

