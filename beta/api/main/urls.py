"""main URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf.urls import url
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from wallets.views import WalletViewSet
from transactions.views import TransactionViewSet, SupplierViewSet, CategorySummaryView
from items.views import ItemViewSet, CategoryViewSet, SubCategoryViewSet
from books.views import BookViewSet


router = routers.DefaultRouter()
router.register(r'wallets', WalletViewSet)
router.register(r'transactions', TransactionViewSet, 'transaction')
router.register(r'suppliers', SupplierViewSet)
router.register(r'items', ItemViewSet)
router.register(r'categorys', CategoryViewSet)
router.register(r'subcategorys', SubCategoryViewSet)
router.register(r'books', BookViewSet)


urlpatterns = [
    path('api/admin/', admin.site.urls),
    path('api/wallets/', include('wallets.urls')),
    path('api/media/', include('media.urls')),
    path('api/transaction/', include('transactions.urls')),
    path('api/auth/', include('rest_framework.urls')),
    path('api/category/summary', CategorySummaryView.as_view()),
    url('api/rest/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
