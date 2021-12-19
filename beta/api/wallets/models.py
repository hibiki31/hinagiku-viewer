from django.db import models


class Wallet(models.Model):
    name = models.CharField(max_length=128, unique=True)
    color = models.CharField(max_length=16, default='#9E9E9E')
    amount = models.IntegerField(default=0)
    code = models.CharField(max_length=16, unique=True, null=True)
    kind = models.CharField(max_length=32)
    is_favorite = models.BooleanField(default=False)
    is_hide = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.pk}: {self.name}'

    __repr__ = __str__
