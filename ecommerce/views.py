from django.views.generic import TemplateView
from hamlpy.views.generic import DetailView, ListView

from ecommerce.models import Product, Cart


class ProductListView(ListView):
    model = Product
    template_name = 'ecommerce/product_list.html.haml'


class ProductDetailView(DetailView):
    model = Product


class UserCartListView(TemplateView):
    template_name = 'ecommerce/cart.html.haml'
    model = Cart

    def get_context_data(self, **kwargs):
        context = super(UserCartListView, self).get_context_data(**kwargs)
        context['cart_list'] = Cart.objects.filter(user=self.request.user)
        return context
