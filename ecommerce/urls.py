from django.urls import path
from django.views.generic import TemplateView

from ecommerce.views import ProductListView, UserCartListView, CartAddView, CartDeleteView, CheckoutPageView

urlpatterns = [
    path('', ProductListView.as_view(), name='home'),
    path('cart/', UserCartListView.as_view(), name='cart'),
    path('cart/add/', CartAddView.as_view(), name='add_to_cart'),
    path('cart/add/failed/',
         TemplateView.as_view(template_name='ecommerce/cannot_add_to_cart.html.haml'), name='cannot_add_to_cart'),
    path('cart/delete/', CartDeleteView.as_view(), name='delete_from_cart'),
    path('checkout/', CheckoutPageView.as_view(), name='checkout'),
]
