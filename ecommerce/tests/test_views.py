import pytest
from django.db import IntegrityError
from django.test import TestCase, RequestFactory
from django.urls import reverse

from ecommerce.models import Product, ProductCategory, Cart, Order, OrderList, Image
from ecommerce.views import get_total_price_of_cart, CheckoutPageView
from registration.models import User


def setup_view(view, request, *args, **kwargs):
    """Mimic ``as_view()``, but returns view instance.
    Use this function to get view instances on which you can run unit tests,
    by testing specific methods."""

    view.request = request
    view.args = args
    view.kwargs = kwargs
    return view


class TestProductListView(TestCase):
    url = reverse('home')

    def populate_products(self):
        self.user = User.objects.create_user(username="Bob", password="12345")
        self.product_1 = Product.objects.create(
            name="Product A", price=100.0, discount_percent=15, quantity=3, rating=4)
        self.product_2 = Product.objects.create(
            name="Product B", price=50.0, discount_percent=10, quantity=2, rating=5)
        self.product_3 = Product.objects.create(
            name="Product C", price=150.0, discount_percent=2, quantity=1, rating=2)
        self.product_4 = Product.objects.create(
            name="Product D", price=990.0, discount_percent=20, quantity=5, rating=1)

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

    def test_banner_image(self):
        self.populate_products()
        Image.objects.create(
            product=self.product_1,
            name=self.product_1.name,
            image_path="",
            image_type=Image.BANNER_IMAGE)
        Image.objects.create(
            product=self.product_2,
            name=self.product_2.name,
            image_path="",
            image_type=Image.BANNER_IMAGE)

        response = self.client.get(self.url)
        self.assertEqual(response.context['banner_image_list'].count(), 2)

    def test_banner_images_greater_than_three(self):
        self.populate_products()
        Image.objects.create(
            product=self.product_1,
            name=self.product_1.name,
            image_path="",
            image_type=Image.BANNER_IMAGE)
        Image.objects.create(
            product=self.product_2,
            name=self.product_2.name,
            image_path="",
            image_type=Image.BANNER_IMAGE)
        Image.objects.create(
            product=self.product_3,
            name=self.product_3.name,
            image_path="",
            image_type=Image.BANNER_IMAGE)
        Image.objects.create(
            product=self.product_4,
            name=self.product_4.name,
            image_path="",
            image_type=Image.BANNER_IMAGE)

        response = self.client.get(self.url)
        self.assertEqual(response.context['banner_image_list'].count(), 3)


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


class EcommerceTestCase(TestCase):

    def login(self):
        self.credentials = {
            'username': 'testuser',
            'password': 'secret@123',
            'wallet_balance': 400
        }
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

    def create_order(self):
        if not (hasattr(self, 'p1') and hasattr(self, 'p2')):
            self.p1 = Product.objects.create(
                name="Product A", price=100.0, discount_percent=15, quantity=3, rating=4)
            self.p2 = Product.objects.create(
                name="Product B", price=230.0, discount_percent=10, quantity=4, rating=4)

        self.order = Order.objects.create(
            user=self.user, amount=(self.p1.discount_price + self.p2.discount_price))
        OrderList.objects.create(order=self.order, product=self.p1, quantity=1)
        OrderList.objects.create(order=self.order, product=self.p2, quantity=1)


class TestCartListView(EcommerceTestCase):
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


class TestCartAddView(EcommerceTestCase):
    url = reverse('add_to_cart')

    def test_redirects_to_login_if_not_logged_in(self):
        response = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(response, template_name='account/login.html.haml')

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

    def test_add_to_cart_product_not_available(self):
        self.login()
        self.create_products()
        self.p1.quantity = 0
        self.p1.save()
        data = {
            'product': self.p1.pk
        }

        response = self.client.post(self.url, data=data, follow=True)
        self.assertTemplateUsed(response, 'ecommerce/cannot_add_to_cart.html.haml')

    def test_add_product_id_not_int(self):
        self.login()
        data = {
            'product': "Not int"
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 404)

    def test_add_product_with_quantity_less_than_required(self):
        self.login()
        self.create_products()

        data = {
            'product': self.p1.pk
        }

        self.client.post(self.url, data=data, follow=True)
        self.p1.quantity = 1
        self.p1.save()

        response = self.client.post(self.url, data=data, follow=True)
        self.assertTemplateUsed(response, 'ecommerce/cannot_add_to_cart.html.haml')


class TestCartDeleteView(EcommerceTestCase):
    url = reverse('delete_from_cart')

    def test_redirects_to_login_if_not_logged_in(self):
        response = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(response, template_name='account/login.html.haml')

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


class TestOrderListView(EcommerceTestCase):
    url = reverse('order_list')

    def test_redirects_to_login_if_not_logged_in(self):
        response = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(response, template_name='account/login.html.haml')

    def test_template_is_correct(self):
        self.login()
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'ecommerce/order_list.html.haml')

    def test_order_list_of_correct_user(self):
        self.login()
        self.create_order()

        response = self.client.get(self.url)
        expected_order = Order.objects.filter(user=self.user)
        self.assertEqual(list(response.context['order_list']), list(expected_order))


class TestOrderDetailView(EcommerceTestCase):

    def test_redirects_to_login_if_not_logged_in(self):
        self.user = User.objects.create(username="User", password="123456")
        self.create_order()
        url = reverse('order_detail', args={self.order.pk})
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, template_name='account/login.html.haml')

    def test_template_is_correct(self):
        self.login()
        self.create_order()
        url = reverse('order_detail', args={self.order.pk})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'ecommerce/order_detail.html.haml')


class TestCheckoutPageView(EcommerceTestCase):
    url = reverse('checkout')

    def test_redirects_to_login_if_not_logged_in(self):
        response = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(response, template_name='account/login.html.haml')

    def test_template_is_correct(self):
        self.login()
        self.create_cart_items()

        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'ecommerce/checkout.html.haml')

    def test_get_cart_list(self):
        self.login()
        self.create_cart_items()

        response = self.client.get(self.url)
        expected_cart_list = Cart.objects.filter(user=self.user)
        self.assertEqual(list(response.context['cart_list']), list(expected_cart_list))

    def test_empty_cart_list(self):
        self.login()

        response = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(response, 'ecommerce/cart.html.haml')

    def test_wallet_balance_in_context(self):
        self.login()
        self.create_cart_items()

        response = self.client.get(self.url)
        self.assertEqual(response.context['wallet_balance'], self.user.wallet_balance)

    def test_total_price_in_context(self):
        self.login()
        self.create_cart_items()
        self.user.wallet_balance = 100
        self.user.save()

        response = self.client.get(self.url)
        self.assertEqual(response.context['wallet_balance'], self.user.wallet_balance)

    def test_checkout_with_empty_cart(self):
        self.login()
        response = self.client.post(self.url, follow=True)
        self.assertTemplateUsed(response, 'ecommerce/cart.html.haml')

    def test_checkout_with_negative_total_cart_amount(self):
        self.login()
        self.create_cart_items()
        self.user.wallet_balance = 0
        self.user.save()

        response = self.client.post(self.url, follow=True)
        self.assertTemplateUsed(response, 'ecommerce/checkout.html.haml')

    def test_redirect_to_order_success(self):
        self.login()
        self.create_cart_items()

        response = self.client.post(self.url, follow=True)
        self.assertTemplateUsed(response, 'ecommerce/order_successful.html.haml')

    def test_order_in_redirect_after_success(self):
        self.login()
        self.create_cart_items()

        response = self.client.post(self.url, follow=True)
        self.assertEqual(response.context['order'], Order.objects.get(user=self.user))

    def test_place_order_from_cart_method_raises_integrity_error_on_None_arguments(self):
        factory = RequestFactory()
        request = factory.get(self.url)

        view = setup_view(CheckoutPageView(), request)
        with self.assertRaises(IntegrityError):
            view.place_order_from_cart(cart_list=None, total_amount=None)

    def test_place_order_from_cart_method_raises_integrity_error_on_0_total(self):
        factory = RequestFactory()
        request = factory.get(self.url)

        view = setup_view(CheckoutPageView(), request)
        with self.assertRaises(IntegrityError):
            view.place_order_from_cart(cart_list=None, total_amount=-1)

        with self.assertRaises(IntegrityError):
            view.place_order_from_cart(cart_list=None, total_amount=0)

    def test_card_list_amount_not_available_raises_integrity_error(self):
        factory = RequestFactory()
        request = factory.get(self.url)

        self.login()
        request.user = self.user

        self.create_cart_items()
        cart_list = Cart.objects.filter(user=self.user)
        self.p1.quantity = 1
        self.p1.save()

        view = setup_view(CheckoutPageView(), request)
        with self.assertRaises(IntegrityError):
            view.place_order_from_cart(
                cart_list=cart_list, total_amount=get_total_price_of_cart(cart_list))
