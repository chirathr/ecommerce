from django.db import models


class Product(models.Model):
    """
    Describes each product
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    price = models.FloatField(default=0.0)
    discount_percent = models.FloatField(default=0.0)
    rating = models.IntegerField(blank=True, null=True)
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Image(models.Model):
    """
    Image associated with a product
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    image_path = models.ImageField(upload_to='products/')
    featured_image = models.BooleanField(default=False)

    def __str__(self):
        return "{0} - {1}".format(self.product.name, self.name)
