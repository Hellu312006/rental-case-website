from django.contrib import admin
from .models import Wishlist

class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'property', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'property__property_name')
    ordering = ('-created_at',)

admin.site.register(Wishlist, WishlistAdmin)
