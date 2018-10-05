from django.urls import path

from ecommerce.views import ProductListView
from registration.views import LoginView

urlpatterns = [
    path('', ProductListView.as_view(), name='home'),
    path('accounts/login/', LoginView.as_view(), name="account_login"),
]
