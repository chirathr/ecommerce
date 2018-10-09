from django.contrib import admin

from ecommerce.models import Image, Product, ProductCategory, Cart, Order, OrderList


class ProductAdmin(admin.ModelAdmin):
    fields = (
        ('name', 'quantity'),
        'description',
        ('price', 'discount_percent'),
        'rating', 'category'
    )

    list_display = ('name', 'price', 'rating')


class ImageAdmin(admin.ModelAdmin):
    list_display = ('name', 'product', 'image_type', 'image_path')


admin.site.register(Product, ProductAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(ProductCategory)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(OrderList)
