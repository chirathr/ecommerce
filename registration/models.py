from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    wallet_balance = models.IntegerField(default=0)

    def reduce_user_wallet_balance(self, order_price):
        if 0 < order_price <= self.wallet_balance:
            self.wallet_balance -= order_price
            self.save()
            return True
        return False
