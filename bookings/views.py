from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from properties.models import Property
from .models import BookingRequest
from .forms import BookingRequestForm

@login_required
def create_booking(request, property_id):
    if request.user.role != 'Tenant':
        messages.error(request, "Access Denied. Only tenants can request bookings.")
        return redirect('property_detail', pk=property_id)
        
    property_obj = get_object_or_404(Property, pk=property_id)
    
    if property_obj.owner == request.user:
        messages.error(request, "You cannot book your own property.")
        return redirect('property_detail', pk=property_id)
        
    if property_obj.available_rooms <= 0:
        messages.error(request, "Sorry, this property has no rooms available for booking.")
        return redirect('property_detail', pk=property_id)

    # Check for duplicate active requests
    existing_booking = BookingRequest.objects.filter(
        tenant=request.user,
        property=property_obj,
        status__in=['Pending', 'Approved']
    ).exists()
    
    if existing_booking:
        messages.warning(request, "You already have a pending or approved booking request for this property.")
        return redirect('property_detail', pk=property_id)

    if request.method == 'POST':
        form = BookingRequestForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.tenant = request.user
            booking.property = property_obj
            booking.status = 'Pending'
            booking.save()
            messages.success(request, f"Booking request for '{property_obj.property_name}' submitted successfully! Awaiting owner approval.")
            return redirect('tenant_dashboard')
        else:
            messages.error(request, "Failed to submit request. Please verify the dates.")
    
    return redirect('property_detail', pk=property_id)


@login_required
@require_POST
def booking_action(request, booking_id, action):
    booking = get_object_or_404(BookingRequest, pk=booking_id)
    
    # Check if logged in user is the owner of the property
    if booking.property.owner != request.user:
        messages.error(request, "Access Denied. You do not own this property.")
        return redirect('dashboard_redirect')
        
    if booking.status != 'Pending':
        messages.warning(request, f"This booking request has already been {booking.status}.")
        return redirect('owner_dashboard')

    if action == 'approve':
        # Check if rooms are available
        if booking.property.available_rooms > 0:
            booking.status = 'Approved'
            booking.save()
            
            # Decrement available rooms
            prop = booking.property
            prop.available_rooms -= 1
            prop.save()
            
            messages.success(request, f"Booking request for {booking.tenant.email} approved successfully!")
        else:
            messages.error(request, "Cannot approve booking: No available rooms left!")
            
    elif action == 'reject':
        booking.status = 'Rejected'
        booking.save()
        messages.success(request, f"Booking request for {booking.tenant.email} has been rejected.")
    else:
        messages.error(request, "Invalid action.")
        
    return redirect('owner_dashboard')
