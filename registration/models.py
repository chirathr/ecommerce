from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

class User(AbstractUser):
    wallet_balance = models.IntegerField(default=0)

    def reduce_user_wallet_balance(self, order_price):
        self.wallet_balance -= order_price
        self.save()
