import wallets
from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection, transaction, models
from rest_framework import viewsets, filters
from rest_framework.response import Response

from .models import Wallet
from .serializers import WalletSerializer

from transactions.models import Transaction
from items.models import Item


class WalletViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.order_by('pk').all()
    serializer_class = WalletSerializer
    pagination_class = None

    def get_serializer_context(self):
        context = super(WalletViewSet, self).get_serializer_context()
        wallets_expenses = Item.objects.values('transaction__wallet_expenses').annotate(amount=models.Sum('amount_expenses')).all()
        wallets_income = Item.objects.values('transaction__wallet_income').annotate(amount=models.Sum('amount_income')).all()
        context.update({"request": self.request, 'income':wallets_income, 'expenses':wallets_expenses})
        return context

def index(request):
    latest_question_list = Wallet.objects

    return HttpResponse(latest_question_list)