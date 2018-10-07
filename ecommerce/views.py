from django.http import Http404
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from hamlpy.views.generic import DetailView, ListView

from ecommerce.models import Product, Cart


class ProductListView(ListView):
    model = Product
    template_name = 'ecommerce/product_list.html.haml'


class ProductDetailView(DetailView):
    model = Product


class UserCartListView(LoginRequiredMixin, TemplateView):
    template_name = 'ecommerce/cart.html.haml'
    model = Cart

    def get_context_data(self, **kwargs):
        context = super(UserCartListView, self).get_context_data(**kwargs)
        context['cart_list'] = Cart.objects.filter(user=self.request.user)
        return context


class UserCartAddView(LoginRequiredMixin, TemplateView):
    success_url = 'cart'
    model = Cart

    def get(self, request, *args):
        return redirect('home')

    def post(self, request, *args):
        if 'product' in request.POST:
            try:
                product = Product.objects.get(pk=int(request.POST['product']))
                if Cart.objects.filter(user=request.user, product=product).count() > 0:
                    cart_item = Cart.objects.get(user=request.user, product=product)
                    cart_item.quantity += 1
                    cart_item.save()
                else:
                    Cart.objects.create(user=request.user, product=product, quantity=1)
            except ValueError:
                raise Http404
            except Product.DoesNotExist:
                raise Http404
        else:
            raise Http404

        return redirect(self.success_url)
