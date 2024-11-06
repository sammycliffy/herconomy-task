from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipient', 'amount', 'transaction_type', 'status', 'created_at')
