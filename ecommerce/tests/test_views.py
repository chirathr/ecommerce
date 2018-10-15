import pytest
from django.test import TestCase
from django.urls import reverse

from ecommerce.models import Product, ProductCategory, Cart
from ecommerce.views import get_total_price_of_cart


# Test ProductListView
from registration.models import User


class TestProductListView(TestCase):
    url = reverse('home')

    def populate_products(self):
        self.user = User.objects.create_user(username="Bob", password="12345")
        self.product_1 = Product.objects.create(
            name="Product A", price=100.0, discount_percent=15, quantity=3, rating=4)
        self.product_2 = Product.objects.create(
            name="Product B", price=50.0, discount_percent=10, quantity=2, rating=5)

    def test_template_is_product_list(self):
        """
        Test is the template used is 'product_list.html.haml'
        :return:
        """
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, template_name='ecommerce/product_list.html.haml')

    def test_template_on_with_empty_db(self):
        """
        Test Empty product db models displays "No Products Found" message
        """
        response = self.client.get(self.url)
        self.assertContains(response, 'No products')

    def test_products_are_shown(self):
        self.populate_products()
        response = self.client.get(self.url)

        self.assertContains(response, 'Product A')
        self.assertContains(response, 'Product B')

    def test_product_categories(self):
        """
        Test a get request with category parameter
        """
        self.populate_products()
        self.product_1.category = ProductCategory.objects.create(name="Category1")
        self.product_1.save()

        response = self.client.get(self.url + '?category=Category1')
        self.assertContains(response, 'Product A')
        self.assertNotContains(response, 'Product B')

    def test_wrong_category(self):
        """
        Test a category that is not there
        """
        self.populate_products()
        response = self.client.get(self.url + '?category=Category1')
        self.assertContains(response, 'No products')


@pytest.mark.django_db
def test_get_total_price_of_cart():
    """
    Test get_total_price_of_cart()
    """
    p1 = Product.objects.create(
        name="Product A", price=100.0, discount_percent=15, quantity=3, rating=4)
    p2 = Product.objects.create(
        name="Product B", price=230.0, discount_percent=10, quantity=4, rating=4)
    user = User.objects.create(username="User", password="12345")

    Cart.objects.create(user=user, product=p1, quantity=2)
    Cart.objects.create(user=user, product=p2, quantity=1)

    expected_total_price = (2 * p1.discount_price) + p2.discount_price
    assert expected_total_price == get_total_price_of_cart(Cart.objects.filter(user=user))


@pytest.mark.django_db
def test_get_total_price_of_cart_with_empty_cart():
    """
    Test empty cart on get_total_price_of_cart()
    """
    user = User.objects.create(username="User", password="12345")
    assert 0 == get_total_price_of_cart(Cart.objects.filter(user=user))


class ProductTestCase(TestCase):

    def login(self):
        self.credentials = {
            'username': 'testuser',
            'password': 'secret@123'}
        self.user = User.objects.create_user(**self.credentials)
        self.client.login(**self.credentials)

    def create_products(self):
        self.p1 = Product.objects.create(
            name="Product A", price=100.0, discount_percent=15, quantity=3, rating=4)
        self.p2 = Product.objects.create(
            name="Product B", price=230.0, discount_percent=10, quantity=4, rating=4)

    def create_cart_items(self):
        if not (hasattr(self, 'p1') and hasattr(self, 'p2')):
            self.p1 = Product.objects.create(
                name="Product A", price=100.0, discount_percent=15, quantity=3, rating=4)
            self.p2 = Product.objects.create(
                name="Product B", price=230.0, discount_percent=10, quantity=4, rating=4)
        Cart.objects.create(user=self.user, product=self.p1, quantity=2)
        Cart.objects.create(user=self.user, product=self.p2, quantity=1)


# Test CardListView
class TestCartListView(ProductTestCase):
    url = reverse('cart')

    def test_redirects_to_login_if_not_logged_in(self):
        response = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(response, template_name='account/login.html.haml')

    def test_template_is_cart(self):
        """
        Check for correct template
        """
        self.login()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='ecommerce/cart.html.haml')

    def test_correct_cart_list_in_context(self):
        self.login()
        self.create_cart_items()

        response = self.client.get(self.url)
        self.assertEqual(
            list(response.context['cart_list']), list(Cart.objects.filter(user=self.user)))

    def test_correct_total_in_context(self):
        self.login()
        self.create_cart_items()

        response = self.client.get(self.url)
        expected_total = get_total_price_of_cart(Cart.objects.filter(user=self.user))
        self.assertEqual(expected_total, response.context['total'])


class TestCartAddView(ProductTestCase):
    url = reverse('add_to_cart')

    def test_get_request_redirects_home(self):
        self.login()
        response = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(response, 'ecommerce/product_list.html.haml')

    def test_add_item_to_cart(self):
        self.login()
        self.create_cart_items()

        expected_product = Product.objects.first()
        data = {
            'product': expected_product.pk
        }

        self.client.post(self.url, data=data)
        cart = Cart.objects.first()
        self.assertEqual(cart.product, expected_product)

    def test_add_item_to_cart_redirects_to_cart(self):
        self.login()
        self.create_products()

        data = {
            'product': Product.objects.first().pk
        }

        response = self.client.post(self.url, data=data, follow=True)
        self.assertTemplateUsed(response, 'ecommerce/cart.html.haml')

    def test_add_item_to_cart_with_unknown_product(self):
        self.login()
        data = {
            'product': 100
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_add_existing_item_to_cart_increases_quantity(self):
        self.login()
        self.create_products()

        data = {
            'product': Product.objects.first().pk
        }
        self.client.post(self.url, data=data, follow=True)
        self.assertEqual(Cart.objects.first().quantity, 1)
        self.client.post(self.url, data=data, follow=True)
        self.assertEqual(Cart.objects.first().quantity, 2)

    def test_wrong_post_request(self):
        self.login()

        data = {}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 404)


class TestCartDeleteView(ProductTestCase):
    url = reverse('delete_from_cart')

    def test_get_request_redirects_home(self):
        self.login()
        response = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(response, 'ecommerce/product_list.html.haml')

    def test_delete_unknown_product_from_cart(self):
        self.login()
        data = {
            'product': 100
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 404)

    def test_delete_from_cart(self):
        self.login()
        self.create_cart_items()

        cart_item = Cart.objects.get(user=self.user, product=self.p1)
        self.assertIn(cart_item, list(Cart.objects.all()))
        data = {
            'product': self.p1.pk
        }
        self.client.post(self.url, data=data)
        self.assertNotIn(cart_item, list(Cart.objects.all()))

    def test_delete_product_id_not_int(self):
        self.login()
        data = {
            'product': "Not int"
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 404)

    def test_delete_product_not_in_cart(self):
        self.login()
        self.create_products()
        data = {
            'product': self.p1.pk
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 404)

    def test_empty_post_request(self):
        self.login()
        data = {}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 404)

# OrderListView
# Returns all orders of correct user
# Test template

# OrderDetailView
# Returns correct template
# Returns correct order with all the products

# CheckOut page View
# Test template
# test get cart list function
# get request
#   - check wallet balance
#   - check cart_list
#   - check total_price
#   - empty cart list redirects to cart
# place order form cart
#   - with empty cart list
#   - Negative total_amount, 0 total_amount
#   - Check if creates correct order with correct items
# post
#   - post with empty cart
#   - post with less wallet balance
#   - check template on success
#   - check order in context
