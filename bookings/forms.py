from django import forms
from .models import BookingRequest
import datetime

class BookingRequestForm(forms.ModelForm):
    class Meta:
        model = BookingRequest
        fields = ['move_in_date', 'duration_months']
        widgets = {
            'move_in_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': datetime.date.today().strftime('%Y-%m-%d') # Browser level validation helper
            }),
            'duration_months': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '36',
                'placeholder': 'Duration (months)'
            }),
        }

    def clean_move_in_date(self):
        move_in_date = self.cleaned_data.get('move_in_date')
        if move_in_date and move_in_date < datetime.date.today():
            raise forms.ValidationError("Move-in date cannot be in the past.")
        return move_in_date

    def clean_duration_months(self):
        duration = self.cleaned_data.get('duration_months')
        if duration and duration <= 0:
            raise forms.ValidationError("Duration must be at least 1 month.")
        return duration
