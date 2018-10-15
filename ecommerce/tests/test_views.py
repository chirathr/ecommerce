import pytest
from django.test import TestCase
from django.urls import reverse

from ecommerce.models import Product, ProductCategory, Cart
from ecommerce.views import get_total_price_of_cart


# Test ProductListView
from registration.models import User


class TestProductListView(TestCase):
    def setUp(self):
        self.url = reverse('home')

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

# Check for correct template
# Check login required
# context['cart_list'] loads correct cart
# context['total'] shows the correct total

# Test CartAddView
# check get request returns home template
# check post request adds item to cart and redirects to cart
# check with unknown product, raises http404
# Check with already existing cart item
# check request without product, raises http404

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
