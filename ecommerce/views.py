from django.http import Http404, HttpResponseServerError
from django.shortcuts import redirect, render
from django.views.generic import TemplateView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction, IntegrityError

from ecommerce.models import Product, Cart, Order, OrderList, ProductCategory, Image


class ProductListView(ListView):
    model = Product
    template_name = 'ecommerce/product_list.html.haml'

    def get_queryset(self):
        if 'category' in self.request.GET:
            category = None
            try:
                category = ProductCategory.objects.get(name=self.request.GET.get("category"))
            except ProductCategory.DoesNotExist:
                return None
            return self.model.objects.filter(category=category)
        else:
            return super(ProductListView, self).get_queryset()

    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super(ProductListView, self).get_context_data(*args, **kwargs)
        banner_image_list = Image.objects.filter(image_type=Image.BANNER_IMAGE).order_by('-name')
        if 'category' not in self.request.GET:
            if banner_image_list.count() <= 3:
                context['banner_image_list'] = banner_image_list
            else:
                # limit to 3 featured images for the carousal
                context['banner_image_list'] = banner_image_list[:3]
        return context


def get_total_price_of_cart(cart_list):
    total = 0
    for cart_item in cart_list:
        total += cart_item.product.discount_price * cart_item.quantity

    return total


class CartListView(LoginRequiredMixin, TemplateView):
    template_name = 'ecommerce/cart.html.haml'
    model = Cart

    def get_context_data(self, **kwargs):
        context = super(CartListView, self).get_context_data(**kwargs)
        context['cart_list'] = Cart.objects.filter(user=self.request.user)
        context['total'] = get_total_price_of_cart(cart_list=context["cart_list"])
        return context


class CartAddView(LoginRequiredMixin, TemplateView):
    success_url = 'cart'
    cannot_add_to_cart_url = 'cannot_add_to_cart'

    def get(self, request, *args):
        return redirect('home')

    def post(self, request, *args):
        if 'product' in request.POST:
            try:
                # Get the product that the user is trying to add to cart
                product = Product.objects.get(pk=int(request.POST['product']))

                # check if product is available
                if product.quantity == 0:
                    return redirect(self.cannot_add_to_cart_url)

                # if already there in cart add quantity
                if Cart.objects.filter(user=request.user, product=product).count() > 0:
                    cart_item = Cart.objects.get(user=request.user, product=product)
                    if cart_item.quantity >= product.quantity:
                        return redirect(self.cannot_add_to_cart_url)
                    cart_item.quantity += 1
                    cart_item.save()

                # Add product to cart
                else:
                    Cart.objects.create(user=request.user, product=product, quantity=1)
            except ValueError:
                raise Http404
            except Product.DoesNotExist:
                raise Http404
        # Wrong request
        else:
            raise Http404("Something went wrong!")

        return redirect(self.success_url)


class CartDeleteView(LoginRequiredMixin, TemplateView):
    success_url = 'cart'

    def get(self, request, *args):
        return redirect('home')

    def post(self, request, *args):
        if 'product' in request.POST:
            try:
                product = Product.objects.get(pk=int(request.POST['product']))
                cart_item = Cart.objects.get(product=product, user=request.user)
                cart_item.delete()

            except ValueError:
                raise Http404
            except Product.DoesNotExist:
                raise Http404
            except Cart.DoesNotExist:
                raise Http404
        # wrong request
        else:
            raise Http404("Something went wrong!")

        return redirect(self.success_url)


class OrderListView(ListView):
    model = Order
    template_name = "ecommerce/order_list.html.haml"

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


class OrderDetailView(DetailView):
    template_name = "ecommerce/order_detail.html.haml"
    model = Order


class CheckoutPageView(LoginRequiredMixin, TemplateView):
    template_name = 'ecommerce/checkout.html.haml'

    def get_cart_list(self):
        return Cart.objects.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):

        cart_list = self.get_cart_list()
        if cart_list.count() == 0:
            # Shows cart is empty
            return redirect('cart')

        context = self.get_context_data()
        context['wallet_balance'] = request.user.wallet_balance
        context['cart_list'] = cart_list
        context['total_price'] = get_total_price_of_cart(cart_list)

        return render(request, self.template_name, context)

    def place_order_from_cart(self, cart_list, total_amount):
        order = Order.objects.create(user=self.request.user, amount=total_amount)

        # Add items in cart to order_list
        for cart_item in cart_list:
            if not cart_item.product.reduce_quantity(cart_item.quantity):
                raise IntegrityError
            OrderList.objects.create(
                order=order, product=cart_item.product, quantity=cart_item.quantity)
            cart_item.delete()

        return order

    def post(self, request, *args, **kwargs):
        cart_list = self.get_cart_list()
        if cart_list.count() == 0:
            # Shows cart is empty
            return redirect('cart')

        total_amount = get_total_price_of_cart(cart_list)

        # Check if wallet balance is there to place the order
        if self.request.user.wallet_balance < total_amount:
            return redirect('checkout')

        # Atomic transaction for placing order
        try:
            with transaction.atomic():
                if not self.request.user.reduce_user_wallet_balance(total_amount):
                    raise IntegrityError
                order = self.place_order_from_cart(cart_list, total_amount)
        except IntegrityError:
            return HttpResponseServerError()

        template_name = "ecommerce/order_successful.html.haml"
        context = {'order': order}

        return render(request, template_name, context)
