from django.db import models
from wallets.models import Wallet


class Supplier(models.Model):
    name = models.CharField(max_length=256, unique=True)

    def __str__(self):
        return f'{self.pk}: {self.name}'


class Transaction(models.Model):
    date = models.DateTimeField()
    kind = models.CharField(max_length=8, default='expenses')
    supplier = models.ForeignKey(
        Supplier,
        related_name='transactions',
        on_delete=models.CASCADE,
        default=1
    )
    wallet_expenses = models.ForeignKey(
        Wallet,
        related_name='transactions_expenses',
        on_delete=models.CASCADE
    )
    wallet_income = models.ForeignKey(
        Wallet,
        related_name='transactions_income',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.pk}: {str(self.date)} {self.supplier}'

    __repr__ = __str__
