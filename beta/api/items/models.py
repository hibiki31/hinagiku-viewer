from django.db import models
from transactions.models import Transaction
    
class Category(models.Model):
    KIND_CHOICES = [
        ('in', 'Income'),
        ('ex', 'Expenses'),
        ('tr', 'Transfer'),
    ]
    name = models.CharField(max_length=16, unique=True)
    code = models.CharField(max_length=16, unique=True)
    kind = models.CharField(max_length=2, choices=KIND_CHOICES, default='in')
    color = models.CharField(max_length=16, default='#9E9E9E')

    def __str__(self):
        return f'{self.pk}: {str(self.name)}'
    
    __repr__ = __str__

class SubCategory(models.Model):
    name = models.CharField(max_length=16, unique=True)
    code = models.CharField(max_length=16, unique=True)
    category = models.ForeignKey(Category, related_name='sub_category', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.pk}: {str(self.name)}'
    
    __repr__ = __str__

class Item(models.Model):
    name = models.CharField(max_length=512)
    amount_income = models.IntegerField(default=0)
    amount_expenses = models.IntegerField(default=0)
    transaction = models.ForeignKey(Transaction, related_name='items', on_delete=models.CASCADE)
    sub_category = models.ForeignKey(SubCategory, related_name='items', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.pk}: {str(self.name)}'
    
    __repr__ = __str__