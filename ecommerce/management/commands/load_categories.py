from django.core.management.base import BaseCommand
from ecommerce.models import ProductCategory


class Command(BaseCommand):
    help = 'Populate db with product categories'

    def handle(self, *args, **options):
        categories = [
            "Laptops",
            "Fruits",
            "Vegetables",
            "Stationery",
            "Mobile",
            "Dress"
        ]

        for category in categories:
            if ProductCategory.objects.filter(name=category).count() > 0:
                continue
            ProductCategory.objects.create(name=category)
