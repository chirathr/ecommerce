from hamlpy.views.generic import HamlExtensionTemplateView
from allauth.account.views import LoginView as BaseLoginView


class LoginView(HamlExtensionTemplateView, BaseLoginView):
    pass
