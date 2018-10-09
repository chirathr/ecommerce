from django.test import TestCase

from ecommerce.models import Product, Image, ProductCategory, Cart, Order, OrderList
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
            product=product, name="image 1", image_path="1.jpg", image_type=Image.FEATURED_IMAGE)

        self.assertEqual(image.image_path, product.featured_image)

    def test_no_featured_image(self):
        product = Product.objects.first()
        self.assertIsNone(product.featured_image)

    def test_multiple_featured_images(self):
        product = Product.objects.first()
        image_1 = Image.objects.create(
            product=product, name="image 1", image_path="1.jpg", image_type=Image.FEATURED_IMAGE)
        image_2 = Image.objects.create(
            product=product, name="image 2", image_path="2.jpg", image_type=Image.FEATURED_IMAGE)

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

    def test_reduce_product_quantity_returns_true(self):
        order_quantity = 5
        initial_quantity = 10
        self.assertEqual(initial_quantity, self.product.quantity)
        self.assertTrue(self.product.reduce_quantity(order_quantity))
        self.assertEqual(initial_quantity - order_quantity, self.product.quantity)

    def test_zero_order_quantity_does_not_change_value(self):
        order_quantity = 0
        initial_quantity = 10
        self.assertFalse(self.product.reduce_quantity(order_quantity))
        self.assertEqual(initial_quantity, self.product.quantity)

    def test_negative_order_quantity_does_not_change_value(self):
        order_quantity = -5
        initial_quantity = 10
        self.assertFalse(self.product.reduce_quantity(order_quantity))
        self.assertEqual(initial_quantity, self.product.quantity)

    def test_order_quantity_greater_than_available_quantity(self):
        order_quantity = 15
        initial_quantity = 10
        self.assertFalse(self.product.reduce_quantity(order_quantity))
        self.assertEqual(initial_quantity, self.product.quantity)


class TestImageModel(TestCase):
    def setUp(self):
        product = Product.objects.create(
            name="Name", price=50.0, discount_percent=9.99, quantity=10)
        Image.objects.create(
            product=product, name="image 1", image_path="1.jpg", image_type=Image.FEATURED_IMAGE)

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

    def test_object_name_is_username_hyphen_product_name(self):
        cart = Cart.objects.first()
        expected_name = "{0} - {1}".format(self.user.username, self.product.name)
        self.assertEqual(expected_name, str(cart))


class TestOrderModel(TestCase):
    def setUp(self):
        self.product1 = Product.objects.create(
            name="Name 1", price=50.0, discount_percent=10, quantity=10, rating=4)
        self.product2 = Product.objects.create(
            name="Name 2", price=55.0, discount_percent=15, quantity=5, rating=2)
        self.user = User.objects.create_user(username="name", password="password")
        self.order = Order.objects.create(user=self.user, amount=105.0)

    def test_object_name_is_username_date(self):
        expected_object_name = "{0} - {0}".format(self.user.username, self.order.date)
        order = Order.objects.first()
        self.assertEqual(expected_object_name, str(order))

    def test_order_list(self):
        OrderList.objects.create(product=self.product1, order=self.order, quantity=1)
        OrderList.objects.create(product=self.product2, order=self.order, quantity=2)

        expected_order_list = OrderList.objects.all().order_by('product')
        actual_order_list = self.order.order_list

        for i in range(len(expected_order_list)):
            self.assertEqual(str(expected_order_list[i]), str(actual_order_list[i]))

    def test_order_list_count(self):
        OrderList.objects.create(product=self.product1, order=self.order, quantity=1)
        OrderList.objects.create(product=self.product2, order=self.order, quantity=2)

        self.assertEqual(OrderList.objects.count(), self.order.order_list_count)


class TestOrderListModel(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Name", price=50.0, discount_percent=10, quantity=10, rating=4)
        self.user = User.objects.create_user(username="name", password="password")
        self.order = Order.objects.create(user=self.user, amount=105.0)
        self.order_list = OrderList.objects.create(
            order=self.order, product=self.product, quantity=1)

    def test_object_name_is_order_comma_product(self):
        expected_object_name = "{0}, {1}".format(self.order, self.product)
        order_list = OrderList.objects.first()

        self.assertEqual(expected_object_name, str(order_list))
