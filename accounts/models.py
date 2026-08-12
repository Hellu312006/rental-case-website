from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('Owner', 'Owner'),
        ('Tenant', 'Tenant'),
    )
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='Tenant')
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)

    REQUIRED_FIELDS = ['first_name', 'last_name']
    USERNAME_FIELD = 'email'
    
    # We will use email as the username, so we must make standard username field optional or override it.
    # In Django, if we set USERNAME_FIELD = 'email', we should make username field email or define it properly.
    # To avoid username conflicts, we can override username to be blank/nullable or set it dynamically in save().
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

class UserProfile(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    phone_no = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    city = models.ForeignKey('properties.City', on_delete=models.SET_NULL, null=True, blank=True)
    state = models.ForeignKey('properties.State', on_delete=models.SET_NULL, null=True, blank=True)
    country = models.ForeignKey('properties.Country', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Profile of {self.user.email}"
