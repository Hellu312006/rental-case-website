from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from properties.models import Property
from .models import Review
from .forms import ReviewForm

@login_required
def add_review(request, property_id):
    # Only tenants can post reviews
    if request.user.role != 'Tenant':
        messages.error(request, "Access Denied. Only tenants can post reviews.")
        return redirect('property_detail', pk=property_id)
        
    property_obj = get_object_or_404(Property, pk=property_id)
    
    # Check for duplicate reviews to meet project requirements
    existing_review = Review.objects.filter(user=request.user, property=property_obj).exists()
    if existing_review:
        messages.warning(request, "You have already reviewed this property.")
        return redirect('property_detail', pk=property_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.property = property_obj
            review.save()
            messages.success(request, "Thank you! Your review has been posted successfully.")
        else:
            messages.error(request, "Failed to submit review. Please check your inputs.")
            
    return redirect('property_detail', pk=property_id)
