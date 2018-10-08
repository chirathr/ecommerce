import random

import requests
import json

from django.core.management.base import BaseCommand
from registration.models import User


class Command(BaseCommand):
    help = 'Populate db with product data from fixture'

    def handle(self, *args, **options):

        r = requests.get('https://uinames.com/api/?amount=20')
        user_data_json = json.loads(r.text)

        for user_data in user_data_json:
            username = str(user_data['name']).lower()
            if User.objects.filter(username=username).count() > 0:
                break

            first_name = str(user_data['name'])
            last_name = str(user_data['surname'])

            User.objects.create_user(
                username=username,
                email="{0}@gmail.com".format(username),
                password="qwerty@123",
                first_name=first_name,
                last_name=last_name,
                wallet_balance=random.randint(100, 10000)
            )
        print("Added 20 random users")
