from django import forms
from .models import RentPayment
from properties.models import Property
from bookings.models import BookingRequest

class RentPaymentForm(forms.ModelForm):
    class Meta:
        model = RentPayment
        fields = ['property', 'amount', 'payment_month', 'payment_method', 'status']
        widgets = {
            'property': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Amount paid'}),
            'payment_month': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. August 2026'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Only show properties for which this tenant has an APPROVED booking request
            approved_properties_ids = BookingRequest.objects.filter(
                tenant=user,
                status='Approved'
            ).values_list('property_id', flat=True)
            self.fields['property'].queryset = Property.objects.filter(id__in=approved_properties_ids)
        else:
            self.fields['property'].queryset = Property.objects.none()
            
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise forms.ValidationError("Payment amount must be greater than zero.")
        return amount
