from django.urls import path

from ecommerce.views import ProductListView

urlpatterns = [
    path('', ProductListView.as_view(), name='home'),
]
