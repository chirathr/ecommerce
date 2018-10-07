import requests
import random
import json
import urllib.request

from django.core.management.base import BaseCommand, CommandError
from ecommerce.models import Product, ProductCategory, Image
from website import settings


class Command(BaseCommand):
    help = 'Populate db with product data from fixture'

    def get_description(self):
        return requests.get('https://loripsum.net/api').text

    def get_image(self, image_prefix, image_suffix, name):
        image_name = "{0}{1}".format(name, image_suffix)
        image_location = "https://www.randomlists.com/{0}{1}".format(image_prefix, image_name)
        image_path = '{0}products/{1}'.format(settings.MEDIA_ROOT, image_name)

        try:
            urllib.request.urlretrieve(image_location, image_path)
            return image_name, "products/{0}".format(image_name)
        except:
            return None, None

    def handle(self, *args, **options):

        categories = ProductCategory.objects.all()

        r = requests.get('https://www.randomlists.com/data/things.json')
        random_list_json = json.loads(r.text)

        items = random_list_json['RandL']['items']

        image_prefix = random_list_json["RandL"]['meta']['img']['prefix']
        image_suffix = random_list_json["RandL"]['meta']['img']['suffix']

        for name in items:

            if Product.objects.filter(name=name).count() > 0:
                continue

            description = self.get_description()
            random_category = categories[random.randint(0, categories.count() - 1)]

            image_name, image_path = self.get_image(image_prefix, image_suffix, name)

            if image_name is None:
                continue

            product = Product.objects.create(
                name=str(name).capitalize(),
                description=description,
                price=random.randint(89, 1000),
                discount_percent=random.randint(0, 100),
                rating=random.randint(0, 5),
                quantity=random.randint(1, 10000),
                category=random_category
            )

            Image.objects.create(product=product, name=image_name, image_path=image_path, featured_image=True)

