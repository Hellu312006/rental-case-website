from django.contrib import admin
from .models import RentPayment

class RentPaymentAdmin(admin.ModelAdmin):
    list_display = ('property', 'user', 'amount', 'payment_month', 'payment_method', 'status', 'payment_date')
    list_filter = ('status', 'payment_method', 'payment_date')
    search_fields = ('property__property_name', 'user__email', 'payment_month')
    ordering = ('-payment_date',)

admin.site.register(RentPayment, RentPaymentAdmin)
