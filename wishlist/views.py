from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from properties.models import Property
from .models import Wishlist

@login_required
@require_POST
def toggle_wishlist(request, property_id):
    property_obj = get_object_or_404(Property, pk=property_id)
    
    # Prevents owners from wishlisting their own properties
    if property_obj.owner == request.user:
        messages.error(request, "You cannot add your own property to your wishlist.")
        return redirect(request.META.get('HTTP_REFERER', 'properties_list'))

    wishlist_item = Wishlist.objects.filter(user=request.user, property=property_obj)
    
    if wishlist_item.exists():
        wishlist_item.delete()
        messages.success(request, f"Removed '{property_obj.property_name}' from your wishlist.")
    else:
        Wishlist.objects.create(user=request.user, property=property_obj)
        messages.success(request, f"Added '{property_obj.property_name}' to your wishlist!")
        
    return redirect(request.META.get('HTTP_REFERER', 'properties_list'))

@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'wishlist/my_wishlist.html', {'wishlist_items': wishlist_items})
