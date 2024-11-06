from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class User(AbstractUser):
    ADMIN = 'admin'
    USER = 'user'
    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (USER, 'User'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=USER, db_index=True)
    balance = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    email = models.EmailField(unique=True, db_index=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set', 
        blank=True,
        help_text='The groups this user belongs to.',
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set', 
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='custom_user',
    )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['username'] 

    def __str__(self):
        return self.username
    
    def save(self, *args, **kwargs):
        if self.balance < 0:
            self.balance = Decimal('0.00')
        self.balance = self.balance.quantize(Decimal('0.00'))
        super().save(*args, **kwargs)
    def is_admin(self):
        return self.role == self.ADMIN

    def is_user(self):
        return self.role == self.USER
