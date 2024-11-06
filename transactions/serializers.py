from rest_framework import serializers
from users.models import User
from .models import Transaction

class TransactionSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all(), required=False)
    recipient = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all(), required=False)
    balance = serializers.DecimalField(source='user.balance', max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Transaction
        fields = ['id', 'user', 'recipient', 'amount', 'transaction_type', 'status', 'created_at', 'balance']


