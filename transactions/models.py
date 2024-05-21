from django.db import models
from accounts.models import UserBankAccount
# Create your models here.
from .constants import TRANSACTION_TYPE, TRANSFER
from django.core.exceptions import ValidationError

class Bankrupt(models.Model):
    is_bankrupt = models.BooleanField(default=False)

    @staticmethod
    def is_bankrupt():
        return Bankrupt.objects.exists() and Bankrupt.objects.first().is_bankrupt
    

class Transaction(models.Model):
    account = models.ForeignKey(UserBankAccount, related_name = 'transactions', on_delete = models.CASCADE) # ekjon user er multiple transactions hote pare
    
    amount = models.DecimalField(decimal_places=2, max_digits = 12)
    balance_after_transaction = models.DecimalField(decimal_places=2, max_digits = 12)
    transaction_type = models.IntegerField(choices=TRANSACTION_TYPE, null = True)
    timestamp = models.DateTimeField(auto_now_add=True)
    loan_approve = models.BooleanField(default=False) 

    
    class Meta:
        ordering = ['timestamp'] 

    @classmethod
    def transfer(cls, sender_account, receiver_account, amount):
        if Bankrupt.is_bankrupt():
            raise ValidationError("The bank is currently bankrupt. Transactions are not allowed.")
        
        if sender_account.balance >= amount:
            sender_account.balance -= amount
            receiver_account.balance += amount
            sender_account.save()
            receiver_account.save()

            # Create and save the Transaction instance
            transaction = cls(account=sender_account, amount=amount, balance_after_transaction=sender_account.balance, transaction_type=TRANSFER)
            transaction.save()
            
            return True
        else:
            return False

    # Add the save method as before
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)