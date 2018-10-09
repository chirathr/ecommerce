from django.db import models
from django.urls import reverse

from registration.models import User


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
    category = models.ForeignKey(
        ProductCategory, on_delete=models.DO_NOTHING, blank=True, null=True)

    def get_absolute_url(self):     # pragma: no cover
        return reverse('product-detail', args=[str(self.pk)])

    @property
    def discount_price(self):
        return self.price - int((self.price * (self.discount_percent / 100)))

    @property
    def stars(self):
        return range(self.rating)

    @property
    def stars_empty(self):
        return range(5 - self.rating)

    @property
    def featured_image(self):
        image = self.image_set.filter(image_type=Image.FEATURED_IMAGE)
        if image.count() > 0:
            return image[0].image_path
        return None

    def reduce_quantity(self, order_quantity):
        if 0 < order_quantity <= self.quantity:
            self.quantity -= order_quantity
            self.save()
            return True
        return False

    def __str__(self):
        return self.name


class Image(models.Model):
    """
    Image associated with a product
    """
    FEATURED_IMAGE = 'FR'
    BANNER_IMAGE = 'BR'
    NORMAL_IMAGE = 'NR'

    IMAGE_TYPE = (
        ('FR', 'Featured Image'),
        ('BR', 'Banner Image'),
        ('NR', 'Normal Image')
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    image_path = models.ImageField(upload_to='products/')
    image_type = models.CharField(max_length=2, choices=IMAGE_TYPE, default=NORMAL_IMAGE)

    def __str__(self):
        return "{0} - {1}".format(self.product.name, self.name)


class Cart(models.Model):
    """
    Shopping cart for users to add products
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return "{0} - {1}".format(self.user.username, self.product.name)


class Order(models.Model):
    """
    Used to store the order when user checkouts
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=False, auto_now_add=True)
    amount = models.FloatField(default=0)

    @property
    def order_list(self):
        return self.orderlist_set.all().order_by('product')

    @property
    def order_list_count(self):
        return len(self.order_list)

    def __str__(self):
        return "{0} - {0}".format(self.user.username, self.date)


class OrderList(models.Model):
    """
    Item in an order
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return "{0}, {1}".format(self.order, self.product)
