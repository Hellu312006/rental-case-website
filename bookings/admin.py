from django.contrib import admin
from .models import BookingRequest

class BookingRequestAdmin(admin.ModelAdmin):
    list_display = ('property', 'tenant', 'move_in_date', 'duration_months', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('property__property_name', 'tenant__email')
    ordering = ('-created_at',)

admin.site.register(BookingRequest, BookingRequestAdmin)
