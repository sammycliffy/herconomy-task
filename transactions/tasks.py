from celery import shared_task
from django.db.models import Sum 
from django.core.mail import send_mail
from .models import Transaction
from django.utils import timezone

from django.conf import settings

from transactions import models
DAILY_LIMIT = 3000000.00
TRANSACTION_THRESHOLD = 10000.00

@shared_task
def verify_transaction(transaction_id):
    try:
        transaction = Transaction.objects.get(id=transaction_id)
        if transaction.transaction_type == 'deposit':
            transaction.status = 'completed'
            transaction.save()
            send_deposit_notification.delay(transaction.id) 
            return
        user = transaction.user
        today_start = timezone.now().replace(hour=0, minute=0, second=0)
        today_end = timezone.now().replace(hour=23, minute=59, second=59)
        daily_total = Transaction.objects.filter(
            user=user,
            created_at__range=(today_start, today_end),
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0  
        if daily_total + transaction.amount > DAILY_LIMIT:
            transaction.status = 'failed'
            transaction.save()
            send_limit_exceeded_notification.delay(transaction.id)  # Send async
            return
        if transaction.transaction_type in ['withdrawal', 'transfer'] and transaction.amount > TRANSACTION_THRESHOLD:
            send_large_transaction_notification.delay(transaction.id)  # Send async
        transaction.status = 'completed'
        transaction.save()
    except Transaction.DoesNotExist:
        return "Transaction not found."
    except Exception as e:
        return f"An error occurred: {str(e)}"



@shared_task
def send_limit_exceeded_notification(transaction_id):
    transaction = Transaction.objects.get(id=transaction_id)
    send_mail(
        'Transaction Limit Exceeded',
        f'Hello {transaction.user.username},\n\nYour transaction of {transaction.amount} '
        'exceeds the daily limit of 10000. Please try a lower amount.',
        settings.DEFAULT_FROM_EMAIL,
        [transaction.user.email],
    )

@shared_task
def send_large_transaction_notification(transaction_id):
    transaction = Transaction.objects.get(id=transaction_id)
    send_mail(
        'Large Transaction Alert',
        f'Hello {transaction.user.username},\n\nA large transaction of {transaction.amount} '
        'was initiated on your account. If this was not you, please contact support immediately.',
        settings.DEFAULT_FROM_EMAIL,
        [transaction.user.email],
    )

@shared_task
def send_deposit_notification(transaction_id):
    transaction = Transaction.objects.get(id=transaction_id)
    send_mail(
        'Deposit Successful',
        f'Hello {transaction.user.username},\n\nYour deposit of {transaction.amount} was successful and '
        'has been credited to your account balance.',
        settings.DEFAULT_FROM_EMAIL,
        [transaction.user.email],
    )