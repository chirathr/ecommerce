from django.urls import path

from ecommerce.views import Home

urlpatterns = [
    path('', Home.as_view(), name='home'),
]
