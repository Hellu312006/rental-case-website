from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import UserProfile
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm
from properties.models import Property, PropertyCategory
from bookings.models import BookingRequest
from payments.models import RentPayment
from wishlist.models import Wishlist

User = get_user_model()

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')
        
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Account created successfully for {user.email}! You can now login.")
            return redirect('login')
        else:
            messages.error(request, "Registration failed. Please correct the errors below.")
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')
        
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name}!")
                return redirect('dashboard_redirect')
            else:
                messages.error(request, "Invalid email or password.")
        else:
            messages.error(request, "Invalid form submission.")
    else:
        form = UserLoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('home')


@login_required
def dashboard_redirect(request):
    if request.user.role == 'Owner':
        return redirect('owner_dashboard')
    else:
        return redirect('tenant_dashboard')


@login_required
def owner_dashboard(request):
    if request.user.role != 'Owner':
        messages.error(request, "Access Denied. You do not have owner privileges.")
        return redirect('tenant_dashboard')
        
    properties = Property.objects.filter(owner=request.user)
    total_properties = properties.count()
    available_properties = properties.filter(available_rooms__gt=0).count()
    
    # Booking requests for properties owned by this user
    booking_requests = BookingRequest.objects.filter(property__owner=request.user).order_by('-created_at')
    total_bookings = booking_requests.count()
    approved_bookings = booking_requests.filter(status='Approved').count()
    pending_requests = booking_requests.filter(status='Pending').count()
    
    # Payments for properties owned by this user
    payments = RentPayment.objects.filter(property__owner=request.user).order_by('-payment_date')
    
    context = {
        'total_properties': total_properties,
        'available_properties': available_properties,
        'total_bookings': total_bookings,
        'approved_bookings': approved_bookings,
        'pending_requests': pending_requests,
        'my_properties': properties[:5],
        'recent_bookings': booking_requests[:5],
        'recent_payments': payments[:5],
    }
    return render(request, 'dashboards/owner_dashboard.html', context)


@login_required
def tenant_dashboard(request):
    if request.user.role != 'Tenant':
        messages.error(request, "Access Denied. Redirecting to owner dashboard.")
        return redirect('owner_dashboard')
        
    wishlist_count = Wishlist.objects.filter(user=request.user).count()
    bookings = BookingRequest.objects.filter(tenant=request.user).order_by('-created_at')
    total_bookings = bookings.count()
    pending_requests = bookings.filter(status='Pending').count()
    approved_bookings = bookings.filter(status='Approved').count()
    
    payments = RentPayment.objects.filter(user=request.user).order_by('-payment_date')
    total_payments = payments.filter(status='Completed').count()
    
    recent_wishlist = Wishlist.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    context = {
        'wishlist_count': wishlist_count,
        'total_bookings': total_bookings,
        'pending_requests': pending_requests,
        'approved_bookings': approved_bookings,
        'total_payments': total_payments,
        'recent_bookings': bookings[:5],
        'recent_wishlist': recent_wishlist,
        'recent_payments': payments[:5],
    }
    return render(request, 'dashboards/tenant_dashboard.html', context)


@login_required
def profile_view(request):
    # Ensure profile exists
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'accounts/profile.html', {'profile': profile})


@login_required
def edit_profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            # Save user first name, last name, and profile image
            user = request.user
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            if form.cleaned_data['profile_image']:
                user.profile_image = form.cleaned_data['profile_image']
            user.save()
            
            # Save profile
            form.save()
            
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('profile')
        else:
            messages.error(request, "Please correct the errors in the profile form.")
    else:
        form = UserProfileForm(instance=profile, user=request.user)
        
    return render(request, 'accounts/edit_profile.html', {'form': form})
