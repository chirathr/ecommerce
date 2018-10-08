from ecommerce.models import ProductCategory


def category_list(request):
    """
    Adds category_list to all pages, to create the list in navbar
    """
    return {'category_list': ProductCategory.objects.all(), }
