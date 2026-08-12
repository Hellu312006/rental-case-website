from django import forms
from django.contrib.auth import get_user_model
from .models import UserProfile
from properties.models import Country, State, City

User = get_user_model()

def validate_image_size(value):
    if value:
        max_size = 5 * 1024 * 1024  # 5MB limit
        if value.size > max_size:
            raise forms.ValidationError("File size cannot exceed 5MB.")
    return value

class UserRegistrationForm(forms.ModelForm):
    profile_image = forms.ImageField(required=False, validators=[validate_image_size], widget=forms.FileInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Create Password'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirm Password'
    }))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'role', 'profile_image']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            # Also create empty profile for the user
            UserProfile.objects.create(user=user)
        return user


class UserLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email Address'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    profile_image = forms.ImageField(required=False, validators=[validate_image_size], widget=forms.FileInput(attrs={'class': 'form-control'}))
    image = forms.ImageField(required=False, validators=[validate_image_size], widget=forms.FileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = UserProfile
        fields = ['phone_no', 'address', 'dob', 'image', 'country', 'state', 'city']
        widgets = {
            'phone_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Address'}),
            'dob': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'country': forms.Select(attrs={'class': 'form-select', 'id': 'id_country'}),
            'state': forms.Select(attrs={'class': 'form-select', 'id': 'id_state'}),
            'city': forms.Select(attrs={'class': 'form-select', 'id': 'id_city'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['profile_image'].initial = user.profile_image
        
        # AJAX/Dynamic location loading setup:
        # If posting or editing, we restrict options based on selection
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
