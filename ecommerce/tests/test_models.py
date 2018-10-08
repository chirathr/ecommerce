from django.test import TestCase

from ecommerce.models import Product, Image, ProductCategory, Cart
from registration.models import User


class TestProductModel(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Name", price=50.0, discount_percent=10, quantity=10, rating=4)

    def test_object_name_is_product_name(self):
        product = Product.objects.first()
        expected_object_name = "Name"
        self.assertEqual(expected_object_name, str(product))

    def test_featured_image_is_returned(self):
        product = Product.objects.first()
        image = Image.objects.create(
            product=product, name="image 1", image_path="1.jpg", featured_image=True)

        self.assertEqual(image.image_path, product.featured_image)

    def test_no_featured_image(self):
        product = Product.objects.first()
        self.assertIsNone(product.featured_image)

    def test_multiple_featured_images(self):
        product = Product.objects.first()
        image_1 = Image.objects.create(
            product=product, name="image 1", image_path="1.jpg", featured_image=True)
        image_2 = Image.objects.create(
            product=product, name="image 2", image_path="2.jpg", featured_image=True)

        expected_images = (image_1.image_path, image_2.image_path)
        self.assertIn(product.featured_image, expected_images)

    def test_discounted_price(self):
        discounted_price = 45
        self.assertEqual(discounted_price, self.product.discount_price)

    def test_starts(self):
        self.product.rating = 3
        self.assertEqual(range(3), self.product.stars)

    def test_empty_start(self):
        self.product.rating = 1
        self.assertEqual(range(4), self.product.stars_empty)


class TestImageModel(TestCase):
    def setUp(self):
        product = Product.objects.create(
            name="Name", price=50.0, discount_percent=9.99, quantity=10)
        Image.objects.create(
            product=product, name="image 1", image_path="1.jpg", featured_image=True)

    def test_object_name_is_product_name_space_image_name(self):
        image = Image.objects.first()
        expected_object_name = "{0} - {1}".format("Name", "image 1")
        self.assertEqual(expected_object_name, str(image))


class TestProductCategoryModel(TestCase):
    def setUp(self):
        ProductCategory.objects.create(name="Category 1")

    def test_object_name_is_category_name(self):
        product_category = ProductCategory.objects.first()
        self.assertEqual("Category 1", str(product_category))


class TestCartModel(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Name", price=50.0, discount_percent=10, quantity=10, rating=4)
        self.user = User.objects.create_user(username="name", password="password")
        self.cart = Cart.objects.create(user=self.user, product=self.product, quantity=1)

    def test_object_name_username_hyphen_product_name(self):
        cart = Cart.objects.first()
        expected_name = "{0} - {1}".format(self.user.username, self.product.name)
        self.assertEqual(expected_name, str(cart))
