from django.db import models


class ProductCategory(models.Model):
    """
    Specific category for each product
    """
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


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
    category = models.ForeignKey(ProductCategory, on_delete=models.DO_NOTHING, blank=True, null=True)

    @property
    def featured_image(self):
        image = self.image_set.filter(featured_image=True)
        if image.count() == 1:
            return image[0].image_path

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
