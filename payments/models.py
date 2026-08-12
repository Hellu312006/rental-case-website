from django.db import models
from django.conf import settings
from properties.models import Property

class RentPayment(models.Model):
    METHOD_CHOICES = (
        ('Credit Card', 'Credit Card'),
        ('Debit Card', 'Debit Card'),
        ('UPI', 'UPI'),
        ('Cash', 'Cash'),
    )
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments")
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="payments")
    amount = models.PositiveIntegerField()
    payment_month = models.CharField(max_length=20)  # e.g., "September 2026"
    payment_method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Pending')
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment of {self.amount} for {self.property.property_name} ({self.status})"
