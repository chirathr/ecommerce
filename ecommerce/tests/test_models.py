from django.test import TestCase

from ecommerce.models import Product, Image


class TestProductModel(TestCase):
    def setUp(self):
        Product.objects.create(
            name="Name", price=50.0, discount_percent=9.99, quantity=10)

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
