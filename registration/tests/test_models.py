from django.test import TestCase

from registration.models import User


class TestUserModel(TestCase):
    def setUp(self):
        self.initial_wallet_balance = 100
        self.user = User.objects.create(
            username="username", password="password", wallet_balance=self.initial_wallet_balance)

    def test_reduce_wallet_balance_returns_true(self):
        user = User.objects.first()
        order_amount = 50

        self.assertEqual(self.initial_wallet_balance, user.wallet_balance)
        self.assertTrue(user.reduce_user_wallet_balance(order_amount))
        self.assertEqual(self.initial_wallet_balance - order_amount, user.wallet_balance)

    def test_reduce_wallet_balance_with_zero_amount(self):
        order_amount = 0
        self.assertFalse(self.user.reduce_user_wallet_balance(order_amount))
        self.assertEqual(self.initial_wallet_balance, self.user.wallet_balance)

    def test_reduce_wallet_balance_with_negative_amount(self):
        order_amount = -50
        self.assertFalse(self.user.reduce_user_wallet_balance(order_amount))
        self.assertEqual(self.initial_wallet_balance, self.user.wallet_balance)

    def test_reduce_wallet_balance_with_more_than_wallet_balance(self):
        order_amount = 150
        self.assertFalse(self.user.reduce_user_wallet_balance(order_amount))
        self.assertEqual(self.initial_wallet_balance, self.user.wallet_balance)
