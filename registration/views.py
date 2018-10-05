from django.shortcuts import render

from hamlpy.views.generic import HamlExtensionTemplateView
from allauth.account.views import LoginView as BaseLoginView

# Create your views here.


class LoginView(HamlExtensionTemplateView, BaseLoginView):
    pass
