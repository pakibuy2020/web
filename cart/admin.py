from django.contrib import admin
from .models import Cart,CartItem,Payment,Shipping
from django.contrib.auth.models import User

# Register your models here.
from django.utils.html import format_html
from django.conf.urls import url
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib import messages
from django.template.response import TemplateResponse

from django.db import transaction

class CartAdmin(admin.ModelAdmin):
    search_fields = ('customer_email','status')
    list_display = ('id','status','net_amt','date_created','action')

    fieldsets = (
        ('Cart', {
            'fields': ('customer_email','status')
        }),
    )

    class Meta:
        model = Cart

    def net_amt(self,obj):
        if obj:
            cart = Cart.objects.get(id=obj.id)
            payment = Payment.objects.get(cart=cart)
            return 'Php. {:20,.2f}'.format(payment.payment_amount)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions     
    def has_delete_permission(self, request, obj=None):
        return False
    def has_add_permission(self, request):
        return False
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["customer_email", "status"]
        else:
            return [] 

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context.update({
            'show_save': False,
            'show_save_and_continue': False,
            'show_delete': False
        })
        return super().render_change_form(request, context, add, change, form_url, obj)
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            url(
                r'^(?P<cart_id>.+)/recieved/$',
                self.admin_site.admin_view(self.process_recieved),
                name='recieved'
            ),
            url(
                r'^(?P<cart_id>.+)/cancel/$',
                self.admin_site.admin_view(self.process_cancel),
                name='cancel'                
            ),
            url(
                r'^(?P<cart_id>.+)/verified/$',
                self.admin_site.admin_view(self.process_verification),
                name='verified'                
            ),
            url(
                r'^(?P<cart_id>.+)/view/$',
                self.admin_site.admin_view(self.view_cart),
                name='view'                
            )
        ]
        return custom_urls + urls

    def action(self, obj):
        status = obj.status
        if status == Cart.STATUS.SHIPPING:
            return format_html(
                '<a class="button" href="{}">Mark as Recieved</a>&nbsp;'
                '<a class="button" href="{}">View Details</a>',
                reverse('admin:recieved', args=[obj.pk]),
                reverse('admin:view', args=[obj.pk])
            )
        elif status == Cart.STATUS.VERIFICATION:
             return format_html(
               '<a class="button" href="{}">Verified</a>&nbsp;'
               '<a class="button" href="{}">Reject</a>&nbsp;'
               '<a class="button" href="{}">View Details</a>',
               reverse('admin:verified', args=[obj.pk]),
               reverse('admin:cancel', args=[obj.pk]),
               reverse('admin:view', args=[obj.pk])
            )           
        elif status == Cart.STATUS.SHOPPING:
            return format_html(
               '<a class="button" href="{}">Cancel Cart</a>&nbsp;'
               '<a class="button" href="{}">View Details</a>',
               reverse('admin:cancel', args=[obj.pk]),
               reverse('admin:view', args=[obj.pk]))

        else:
           return format_html(
                '<a class="button" href="{}">View Details</a>',
                reverse('admin:view', args=[obj.pk])
            )
    action.short_description = "Order Actions"
    action.allow_tags = True

    def view_cart(self, request,cart_id, *args, **kwargs):
        context = self.admin_site.each_context(request)
        context['opts'] = self.model._meta

        cart = Cart.objects.get(id=cart_id)
        cartItems = CartItem.objects.filter(cart=cart)
        
        custname = User.objects.get(email=cart.customer_email)

        context['custname'] = custname
        context['cart'] = cart
        context['cartItems'] = cartItems

        try:
            shipping = Shipping.objects.get(cart=cart)
            context['shipping'] = shipping
        except Shipping.DoesNotExist:
            pass
        
        return TemplateResponse(request,'admin/cart/view.html',context)

    # once the status is shipping. Cart can now mark as recieved
    @transaction.atomic
    def process_recieved(self, request,cart_id, *args, **kwargs):
        try:
            Cart.objects.filter(id=cart_id).update(status=Cart.STATUS.RECIEVED)
            cart = Cart.objects.get(id=cart_id)

            # if COD then update payment
            payment = Payment.objects.get(cart=cart)
            if payment.payment_type == Payment.PAYMENT_TYPE.COD:
                Payment.objects.filter(cart=cart).update(payment_status=Payment.PAYMENT_STATUS.PAID)

            messages.success(request, 'Cart successfully marked as Recieved')
        except Cart.DoesNotExist:
            messages.add_message(request, messages.SUCCESS, 'Cart cannot mark as recieved.')
        
        return redirect('/admin/cart/cart/')

    # once the status is verification. User can mark it as verified
    # only for COD payment
    @transaction.atomic
    def process_verification(self, request,cart_id, *args, **kwargs):
        try:
            Cart.objects.filter(id=cart_id).update(status=Cart.STATUS.SHIPPING)
            messages.success(request, 'Cart successfully verified')
        except Cart.DoesNotExist:
            messages.add_message(request, messages.SUCCESS, 'Cart cannot mark as verified.')
        
        return redirect('/admin/cart/cart/')

    # if the status is shopping. Can can mark as cancel by admin
    @transaction.atomic
    def process_cancel(self, request,cart_id, *args, **kwargs):
        try:
            Cart.objects.filter(id=cart_id).update(status=Cart.STATUS.CANCELLED)
            cart = Cart.objects.get(id=cart_id)
            Payment.objects.filter(cart=cart).update(payment_status=Payment.PAYMENT_STATUS.CANCELLED)
            messages.success(request, 'Cart successfully marked as Cancel')
        except Cart.DoesNotExist:
            messages.add_message(request, messages.SUCCESS, 'Cart cannot mark as cancel.')
        
        return redirect('/admin/cart/cart/')

class PaymentAdmin(admin.ModelAdmin):
    search_fields = ('payment_type','payment_status','paymongo_id','date_created')
    list_display = ('id','cart','paymongo_id','net','payment_type','payment_status','date_created','free_shipping')

    class Meta:
        model = Payment

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions     
    def has_delete_permission(self, request, obj=None):
        return False
    def has_add_permission(self, request):
        return False
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["paymongo_id", "cart","net",'payment_amount','payment_type','payment_status','free_shipping']
        else:
            return [] 
    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context.update({
            'show_save': False,
            'show_save_and_continue': False,
            'show_delete': False
        })
        return super().render_change_form(request, context, add, change, form_url, obj)  

class ShippingAdmin(admin.ModelAdmin):
    class Meta:
        model = Shipping

admin.site.register(Cart,CartAdmin)
admin.site.register(Shipping,ShippingAdmin)
admin.site.register(Payment,PaymentAdmin)