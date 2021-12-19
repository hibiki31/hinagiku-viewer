from django.db.models.expressions import Subquery
from wallets.models import Wallet
from django_filters import rest_framework as filters
from django.core import serializers
from django.db import connection, transaction, models
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
import json
from .models import Transaction, Supplier
from items.models import Item, Category, SubCategory
from .serializers import TransactionSerializer, SupplierSerializer
import csv
import io
from datetime import datetime


class SupplierFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr='contains')

    class Meta:
        model = Supplier
        fields = ['name']


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer

    def get_queryset(self):
        queryset = Transaction.objects.order_by('date','-pk').reverse().all()
        if (name := self.request.query_params.get('name')) is not None:
            queryset = queryset.filter(items__name__icontains=name)
        if (supplier := self.request.query_params.get('supplier')) is not None:
            queryset = queryset.filter(supplier__name__icontains=supplier)
        if (category := self.request.query_params.get('category')) is not None:
            queryset = queryset.filter(items__sub_category__category__pk=category)
        if (subcategory := self.request.query_params.get('subcategory')) is not None:
            queryset = queryset.filter(items__sub_category__pk=subcategory)
        if (wallet := self.request.query_params.get('wallet')) is not None:
            queryset = queryset.filter(Q(wallet_income=wallet) | Q(wallet_expenses=wallet))
        if (kind := self.request.query_params.get('kind')) is not None:
            queryset = queryset.filter(kind=kind)
        if (year := self.request.query_params.get('year')) is not None:
            queryset = queryset.filter(date__year=year)
        if (month := self.request.query_params.get('month')) is not None:
            queryset = queryset.filter(date__month=month)
        return queryset.distinct()


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    pagination_class = None
    filter_class = SupplierFilter


class CategorySummaryView(APIView):
    def get(self, request, format=None):
        
        transaction = Item.objects.filter(
                transaction__date__year=request.query_params.get('year','2021')
            ).values(
            month=models.F('transaction__date__month'),
            category_name=models.F('sub_category__category__name'), 
            category_id=models.F('sub_category__category__pk')
            ).annotate(
                amount=models.Sum('amount_expenses')
            ).all()
        
        sum_dict = {}

        for i in transaction:
            if not i['category_id'] in sum_dict:
                sum_dict[i['category_id']] = {}
            sum_dict[i['category_id']][i['month']] = i["amount"]

        
        category = Category.objects.all()

        result_list = []
        for i in category:
            summary = []
            for j in range(1, 12 + 1):
                try:
                    amount = sum_dict[i.pk][j]
                except:
                    amount = 0
                summary.append(amount)
            row = {
                    "name": i.name,
                    "pk": i.pk,
                    "color": i.color,
                    "summary": summary
            }
            result_list.append(row)
        
        return Response(result_list)
        return Response(json.loads(serializers.serialize('json', transaction)))

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

@csrf_exempt
def import_csv(request):
    if request.method == 'POST':
        data = io.TextIOWrapper(request.FILES['file'].file, encoding='utf-8-sig')
        csv_content = list(csv.reader(data))

        csv_type = request.POST.get('type')

        if csv_type == 'rakuten_card':
            return import_rakuten_card(request,csv_content)
        elif csv_type == 'pasmo':
            return import_pasmo(request,csv_content)
        else:
            return HttpResponse({"error"})
    
    return HttpResponse({"plz post"})

    
    


def import_rakuten_card(request, csv_content):
    print(csv_content[0][0])
    if '利用日' != csv_content[0][0]:
        return HttpResponse({"error"})
    for i in csv_content:
        if i[0] == '利用日' or i[0] == '':
            continue
        
        transaction = Transaction(
            date = datetime.strptime(i[0], "%Y/%m/%d"),
            wallet_income = Wallet(pk=int(request.POST.get('wallet', None))),
            wallet_expenses = Wallet(pk=int(request.POST.get('wallet', None))),
            supplier = Supplier(pk=int(request.POST.get('supplier', None)))
        )
        transaction.save()
        item = Item(
            name = i[1],
            amount_income = 0,
            amount_expenses = int(i[7]),
            transaction = transaction,
            sub_category = SubCategory(pk=int(request.POST.get('subcategory', None)))
        )
        item.save()
    return HttpResponse({"success"})

def import_pasmo(request, csv_content):
    if ['月/日', '種別', '利用場所', '種別', '利用場所', '残額', '差額'] != csv_content[0]:
        return HttpResponse({"type error"})
    for i in csv_content:
        if i[0] == '月/日' or i[0] == '':
            continue
        if i[1] == '繰':
            continue

        amount = -int(i[6].replace(",", ""))
        if amount < 0:
            kind = 'transfer'
            name = f'{i[1]} {i[2]}'
            amount_income = -amount
        elif i[1] == '物販':
            kind = 'expenses'
            name = '物販'
            amount_income = 0
        else:
            kind = 'expenses'
            name = f'{i[1]} {rep(i[2])} {i[3]} {rep(i[4])}'
            amount_income = 0

        transaction = Transaction(
            date = datetime.strptime(i[0], "%Y/%m/%d"),
            wallet_income = Wallet(pk=int(request.POST.get('wallet', None))),
            wallet_expenses = Wallet(pk=int(request.POST.get('wallet', None))),
            supplier = Supplier(pk=int(request.POST.get('supplier', None))),
            kind = kind
        )
        transaction.save()
        item = Item(
            name = name,
            amount_income = amount_income,
            amount_expenses = amount,
            transaction = transaction,
            sub_category = SubCategory(pk=int(request.POST.get('subcategory', None)))
        )
        item.save()
    return HttpResponse({"success"})

def rep(txt):
    return txt.replace("\u3000", " ")