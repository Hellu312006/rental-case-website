from django import forms
from .models import Property, PropertyImages, Country, State, City

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            'property_name', 'category', 'property_type', 'description', 
            'address', 'country', 'state', 'city', 
            'rent_per_month', 'security_deposit', 'available_rooms', 'total_rooms', 
            'image'
        ]
        widgets = {
            'property_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter property title'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'property_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Detailed description of the property...'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Street address...'}),
            'country': forms.Select(attrs={'class': 'form-select', 'id': 'id_country'}),
            'state': forms.Select(attrs={'class': 'form-select', 'id': 'id_state'}),
            'city': forms.Select(attrs={'class': 'form-select', 'id': 'id_city'}),
            'rent_per_month': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Monthly rent amount'}),
            'security_deposit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Security deposit amount'}),
            'available_rooms': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Rooms currently available'}),
            'total_rooms': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Total rooms in property'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Limit states and cities in dynamic dropdowns
        if 'country' in self.data:
            try:
                country_id = int(self.data.get('country'))
                self.fields['state'].queryset = State.objects.filter(country_id=country_id).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.country:
            self.fields['state'].queryset = self.instance.country.states.order_by('name')
        else:
            self.fields['state'].queryset = State.objects.none()

        if 'state' in self.data:
            try:
                state_id = int(self.data.get('state'))
                self.fields['city'].queryset = City.objects.filter(state_id=state_id).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.state:
            self.fields['city'].queryset = self.instance.state.cities.order_by('name')
        else:
            self.fields['city'].queryset = City.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        rent = cleaned_data.get('rent_per_month')
        deposit = cleaned_data.get('security_deposit')
        available = cleaned_data.get('available_rooms')
        total = cleaned_data.get('total_rooms')

        if rent is not None and rent <= 0:
            self.add_error('rent_per_month', "Rent must be greater than zero.")
        if deposit is not None and deposit < 0:
            self.add_error('security_deposit', "Security deposit cannot be negative.")
        if available is not None and total is not None:
            if available > total:
                self.add_error('available_rooms', "Available rooms cannot exceed total rooms.")
        return cleaned_data


class PropertyImageForm(forms.ModelForm):
    class Meta:
        model = PropertyImages
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }
