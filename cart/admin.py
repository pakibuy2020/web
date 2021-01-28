from django.contrib import admin
from .models import Cart,CartItem,Payment
# Register your models here.

class CartAdmin(admin.ModelAdmin):
    search_fields = ('customer_email','status')
    list_display = ('id','status','net_amt','date_created')

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

# class DeliveryAdmin(admin.ModelAdmin):
#     class Meta:
#         model = Delivery

admin.site.register(Cart,CartAdmin)
# admin.site.register(Delivery,DeliveryAdmin)
admin.site.register(Payment,PaymentAdmin)