from django.urls import path

from ecommerce.views import ProductListView, UserCartListView, UserCartAddView, UserCartDeleteView

urlpatterns = [
    path('', ProductListView.as_view(), name='home'),
    path('cart/', UserCartListView.as_view(), name='cart'),
    path('cart/add/', UserCartAddView.as_view(), name='add_to_cart'),
    path('cart/delete/', UserCartDeleteView.as_view(), name='delete_from_cart'),
]
