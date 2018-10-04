from django.shortcuts import render

from hamlpy.views.generic import DetailView, ListView

from ecommerce.models import Product


class ProductListView(ListView):
    model = Product
