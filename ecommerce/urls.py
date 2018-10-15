from django.urls import path
from django.views.generic import TemplateView

from ecommerce.views import ProductListView, CartListView, CartAddView, \
    CartDeleteView, CheckoutPageView, OrderListView, OrderDetailView

urlpatterns = [
    path('', ProductListView.as_view(), name='home'),
    path('cart/', CartListView.as_view(), name='cart'),
    path('cart/add/', CartAddView.as_view(), name='add_to_cart'),
    path('cart/add/failed/', TemplateView.as_view(
        template_name='ecommerce/cannot_add_to_cart.html.haml'), name='cannot_add_to_cart'),
    path('cart/delete/', CartDeleteView.as_view(), name='delete_from_cart'),
    path('checkout/', CheckoutPageView.as_view(), name='checkout'),
    path('order/', OrderListView.as_view(), name='order_list'),
    path('order/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('checkout/failed/', TemplateView.as_view(
        template_name='ecommerce/checkout_failed.html.haml'), name='checkout_failed'),
]
