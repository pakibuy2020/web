from django.contrib import admin
from django.forms import ModelForm
from .models import Product,Supplier,Stock
# from dynamic_raw_id.admin import DynamicRawIDMixin

class SupplierAdmin(admin.ModelAdmin):
    search_fields = ('id','name',)
    class Meta:
        model = Supplier
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions        

# admin view of product
class ProductAdmin(admin.ModelAdmin):
    list_display = ('sku','name','price','current_stock')
    search_fields = ('sku','name','price')

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    class Meta:
        model = Product

class StockAdmin(admin.ModelAdmin):
    search_fields = ('id','product__name','last_updated')
    list_display = ('id','product','last_updated')
    fieldsets = (
        ('Product', {
            'fields': ('product',)
        }),
        ('Supplier & Stock', {
            'fields': ('supplier','stock')
        })
    )
    class Meta:
        model = Stock

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["product", "supplier"]
        else:
            return []        
    
# class CategoryAdmin(admin.ModelAdmin):
#     search_fields = ('id','name')
#     def get_actions(self, request):
#         actions = super().get_actions(request)
#         if 'delete_selected' in actions:
#             del actions['delete_selected']
#         return actions

#     class Meta:
#         model = Category    

# admin.site.register(Category,CategoryAdmin)
admin.site.register(Supplier,SupplierAdmin)
admin.site.register(Product,ProductAdmin)
admin.site.register(Stock,StockAdmin)
