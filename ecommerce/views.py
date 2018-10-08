from django.http import Http404
from django.shortcuts import redirect, render
from django.views.generic import TemplateView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from ecommerce.models import Product, Cart, Order, OrderList, ProductCategory


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


class ProductDetailView(DetailView):
    model = Product


def get_total_price_of_cart(cart_list):
    total = 0
    for cart_item in cart_list:
        total += cart_item.product.discount_price * cart_item.quantity

    return total


class UserCartListView(LoginRequiredMixin, TemplateView):
    template_name = 'ecommerce/cart.html.haml'
    model = Cart

    def get_context_data(self, **kwargs):
        context = super(UserCartListView, self).get_context_data(**kwargs)
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

    def reduce_user_balance(self, order_price):
        self.request.user.wallet_balance -= order_price
        self.request.user.save()

    def place_order_from_cart(self, cart_list, total_amount):
        order = Order.objects.create(user=self.request.user, amount=total_amount)

        # Add items in cart to order_list
        for cart_item in cart_list:
            OrderList.objects.create(order=order, product=cart_item.product, quantity=cart_item.quantity)
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

        self.reduce_user_balance(total_amount)
        order = self.place_order_from_cart(cart_list, total_amount)

        template_name = "ecommerce/order_successful.html.haml"
        context = {'order': order}

        return render(request, template_name, context)
