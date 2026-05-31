from django.contrib import admin
from django_ecomm_app.models import Category,Product,Cart,CartItem,Order,OrderItem

# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display=['pr_name','pr_category','pr_price','is_featured','pr_stock']
    list_editable=['pr_price','pr_stock','is_featured']
    list_filter=['pr_category']
    search_fields=['pr_name']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display=['id','user','ord_total_price','ord_status','ord_created_at']
    list_editable=['ord_status']

admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(OrderItem)