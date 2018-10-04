from django.contrib import admin

from ecommerce.models import Image, Product, ProductCategory


class ProductAdmin(admin.ModelAdmin):
    fields = (
        ('name', 'quantity'),
        'description',
        ('price', 'discount_percent'),
        'rating', 'category'
    )

    list_display = ('name', 'price', 'rating')


class ImageAdmin(admin.ModelAdmin):
    list_display = ('name', 'product', 'featured_image')


admin.site.register(Product, ProductAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(ProductCategory)
