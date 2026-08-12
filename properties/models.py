from django.db import models
from django.conf import settings

class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Countries"

    def __str__(self):
        return self.name

class State(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="states")
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('country', 'name')

    def __str__(self):
        return f"{self.name}, {self.country.name}"

class City(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name="cities")
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Cities"
        unique_together = ('state', 'name')

    def __str__(self):
        return f"{self.name}, {self.state.name}"

class PropertyCategory(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)

    class Meta:
        verbose_name_plural = "Property Categories"

    def __str__(self):
        return self.category_name

class Property(models.Model):
    PROPERTY_TYPE_CHOICES = (
        ('PG', 'PG'),
        ('Flat', 'Flat'),
        ('House', 'House'),
        ('Hostel', 'Hostel'),
    )
    
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="properties")
    category = models.ForeignKey(PropertyCategory, on_delete=models.CASCADE, related_name="properties")
    property_name = models.CharField(max_length=200)
    description = models.TextField()
    address = models.TextField()
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    rent_per_month = models.PositiveIntegerField()
    security_deposit = models.PositiveIntegerField()
    available_rooms = models.PositiveIntegerField()
    total_rooms = models.PositiveIntegerField()
    property_type = models.CharField(max_length=10, choices=PROPERTY_TYPE_CHOICES)
    image = models.ImageField(upload_to='property_images/')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Properties"

    def __str__(self):
        return self.property_name

    @property
    def image_url(self):
        try:
            if self.image and self.image.storage.exists(self.image.name):
                return self.image.url
        except Exception:
            pass

        # Fallback to direct unsplash URLs based on name matches
        name = self.property_name.lower()
        if 'sunset' in name or 'guest' in name:
            return 'https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af?q=80&w=800&auto=format&fit=crop'
        elif 'villa' in name or 'garden' in name:
            return 'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?q=80&w=800&auto=format&fit=crop'
        elif 'silicon' in name or 'premium' in name:
            return 'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?q=80&w=800&auto=format&fit=crop'
        elif 'hostel' in name or 'living' in name:
            return 'https://images.unsplash.com/photo-1555854877-bab0e564b8d5?q=80&w=800&auto=format&fit=crop'
        elif 'ahmedabad' in name or 'heights' in name:
            return 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?q=80&w=800&auto=format&fit=crop'
        elif 'rajkot' in name or 'cozy' in name:
            return 'https://images.unsplash.com/photo-1598928506311-c55ded91a20c?q=80&w=800&auto=format&fit=crop'
        
        return 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?q=80&w=800&auto=format&fit=crop'

class PropertyImages(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='property_gallery/')

    class Meta:
        verbose_name_plural = "Property Images"

    def __str__(self):
        return f"Image for {self.property.property_name}"
