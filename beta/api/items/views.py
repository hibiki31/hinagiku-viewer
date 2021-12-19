from wallets import serializers
from django.shortcuts import render
from rest_framework import viewsets, filters

from .models import Item, Category, SubCategory
from .serializers import ItemSerializer, CategorySerializer, SubCategorySerializer

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.order_by('pk').all()
    serializer_class = CategorySerializer
    pagination_class = None

class SubCategoryViewSet(viewsets.ModelViewSet):
    queryset = SubCategory.objects.order_by('pk').all()
    serializer_class = SubCategorySerializer
    pagination_class = None
