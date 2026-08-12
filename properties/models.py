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

class PropertyImages(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='property_gallery/')

    class Meta:
        verbose_name_plural = "Property Images"

    def __str__(self):
        return f"Image for {self.property.property_name}"
