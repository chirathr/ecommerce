from django.urls import path

from ecommerce.views import ProductListView,UserCartListView

urlpatterns = [
    path('', ProductListView.as_view(), name='home'),
    path('cart/', UserCartListView.as_view(), name='cart_list'),
]
