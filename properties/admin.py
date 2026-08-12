from django.contrib import admin
from .models import Country, State, City, PropertyCategory, Property, PropertyImages

class PropertyImagesInline(admin.TabularInline):
    model = PropertyImages
    extra = 3

class PropertyAdmin(admin.ModelAdmin):
    list_display = ('property_name', 'owner', 'category', 'property_type', 'rent_per_month', 'city', 'available_rooms')
    list_filter = ('property_type', 'category', 'city', 'state', 'country')
    search_fields = ('property_name', 'owner__email', 'city__name', 'address')
    inlines = [PropertyImagesInline]

class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'state')
    list_filter = ('state',)
    search_fields = ('name',)

class StateAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')
    list_filter = ('country',)
    search_fields = ('name',)

admin.site.register(Country)
admin.site.register(State, StateAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(PropertyCategory)
admin.site.register(Property, PropertyAdmin)
admin.site.register(PropertyImages)
