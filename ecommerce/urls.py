from django.urls import path

from ecommerce.views import ProductListView, UserCartListView, UserCartAddView

urlpatterns = [
    path('', ProductListView.as_view(), name='home'),
    path('cart/', UserCartListView.as_view(), name='cart'),
    path('cart/add/', UserCartAddView.as_view(), name='add_to_cart'),
]
