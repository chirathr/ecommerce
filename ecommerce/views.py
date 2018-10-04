from django.shortcuts import render

# Create your views here.
from django.views.generic import TemplateView
from hamlpy.views.generic import HamlExtensionTemplateView


class Home(HamlExtensionTemplateView, TemplateView):
    template_name = 'base/base.haml'
