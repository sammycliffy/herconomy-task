from rest_framework import permissions, status, pagination
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction as db_transaction
from users.models import User
from .models import Transaction
from .serializers import TransactionSerializer
from .tasks import verify_transaction

class TransactionPagination(pagination.PageNumberPagination):
    page_size = 10  
    page_size_query_param = 'page_size'
    max_page_size = 100

class TransactionView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = TransactionPagination

    def get_queryset(self, user):
        if user.role == 'admin':
           username = self.request.query_params.get('username')
           if username:
                return Transaction.objects.filter(user__username=username).order_by('-created_at')
           return Transaction.objects.all().order_by('-created_at')
        return Transaction.objects.filter(user=user).order_by('-created_at')

    def get(self, request):
        transactions = self.get_queryset(request.user)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(transactions, request)
        serializer = TransactionSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            transaction_type = serializer.validated_data.get('transaction_type')
            if transaction_type == 'deposit':
                return self.deposit(serializer)
            elif transaction_type == 'withdrawal':
                return self.withdraw(serializer)
            elif transaction_type == 'transfer':
                recipient_username = request.data.get('recipient')
                return self.transfer(serializer, recipient_username)
            return Response({"detail": "Invalid transaction type."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def deposit(self, serializer):
        with db_transaction.atomic():
            user = self.request.user
            amount = serializer.validated_data['amount']
            if amount <= 0:
                return Response({"detail": "Deposit amount must be positive."}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save(user=user, status='pending') 
            user.balance += amount
            user.save()
            verify_transaction.delay(serializer.instance.id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def withdraw(self, serializer):
        with db_transaction.atomic():
            user = self.request.user
            amount = serializer.validated_data['amount']
            if amount <= 0:
                return Response({"detail": "Withdrawal amount must be positive."}, status=status.HTTP_400_BAD_REQUEST)
            if user.balance < amount:
                return Response({"detail": "Insufficient funds."}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save(user=user, status='pending')
            user.balance -= amount
            user.save()
            verify_transaction.delay(serializer.instance.id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def transfer(self, serializer, recipient_username):
        try:
            recipient = User.objects.get(username=recipient_username)
        except User.DoesNotExist:
            return Response({"detail": "Recipient not found."}, status=status.HTTP_404_NOT_FOUND)
        
        if recipient == self.request.user:
            return Response({"detail": "Cannot transfer to oneself."}, status=status.HTTP_400_BAD_REQUEST)
        
        with db_transaction.atomic():
            user = self.request.user
            amount = serializer.validated_data['amount']
            if amount <= 0:
                return Response({"detail": "Transfer amount must be positive."}, status=status.HTTP_400_BAD_REQUEST)
            if user.balance >= amount:
                serializer.save(user=user, status='pending') 
                user.balance -= amount
                recipient.balance += amount
                user.save()
                recipient.save()
                Transaction.objects.create(
                    user=recipient,
                    amount=amount,
                    transaction_type='transfer',
                    status='pending', 
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({"detail": "Insufficient funds."}, status=status.HTTP_400_BAD_REQUEST)
