from django.http import Http404
from django.shortcuts import redirect, render
from django.views.generic import TemplateView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from ecommerce.models import Product, Cart, Order


class ProductListView(ListView):
    model = Product
    template_name = 'ecommerce/product_list.html.haml'


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

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


class OrderDetailView(DetailView):
    model = Order


class CheckoutPageView(LoginRequiredMixin, TemplateView):
    template_name = 'ecommerce/checkout.html.haml'

    def get(self, request, *args, **kwargs):
        cart_list = Cart.objects.filter(user=request.user)

        # If cart is empty
        if cart_list.count() == 0:
            # Shows cart is empty
            return redirect('cart')

        context = self.get_context_data()

        context['wallet_balance'] = request.user.wallet_balance
        context['cart_list'] = Cart.objects.filter(user=self.request.user)
        context['total_price'] = get_total_price_of_cart(cart_list=context["cart_list"])

        return render(request, self.template_name, context)
