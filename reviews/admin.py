from django.contrib import admin
from .models import Review

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('property', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('property__property_name', 'user__email', 'comment')
    ordering = ('-created_at',)

admin.site.register(Review, ReviewAdmin)
