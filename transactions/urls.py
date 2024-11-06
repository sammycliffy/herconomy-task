from django.urls import path, include
from rest_framework.routers import DefaultRouter
from transactions.views import TransactionView




urlpatterns = [
       path('transactions/', TransactionView.as_view(), name='transactions'),
]
