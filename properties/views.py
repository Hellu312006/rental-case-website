from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Q, Count
from django.core.paginator import Paginator
from django.forms import inlineformset_factory
from django.http import JsonResponse

from .models import Property, PropertyCategory, Country, State, City, PropertyImages
from .forms import PropertyForm, PropertyImageForm
from reviews.models import Review
from wishlist.models import Wishlist
from bookings.models import BookingRequest

# Home View
def home_view(request):
    categories = PropertyCategory.objects.annotate(prop_count=Count('properties'))
    featured_properties = Property.objects.annotate(avg_rating=Avg('reviews__rating')).order_by('-created_at')[:6]
    
    wishlisted_ids = []
    if request.user.is_authenticated:
        wishlisted_ids = Wishlist.objects.filter(user=request.user).values_list('property_id', flat=True)

    return render(request, 'home.html', {
        'categories': categories,
        'featured_properties': featured_properties,
        'wishlisted_ids': list(wishlisted_ids),
    })


# AJAX Views for Location Cascading
def load_states(request):
    country_id = request.GET.get('country_id')
    states = State.objects.filter(country_id=country_id).order_by('name')
    return JsonResponse(list(states.values('id', 'name')), safe=False)

def load_cities(request):
    state_id = request.GET.get('state_id')
    cities = City.objects.filter(state_id=state_id).order_by('name')
    return JsonResponse(list(cities.values('id', 'name')), safe=False)


# Main Properties Directory (with Search, Filter, Sort, Pagination)
def properties_list(request):
    properties = Property.objects.annotate(avg_rating=Avg('reviews__rating')).order_by('-created_at')

    # Get filter choices
    countries = Country.objects.all()
    states = State.objects.all()
    cities = City.objects.all()
    categories = PropertyCategory.objects.all()
    property_types = ['PG', 'Flat', 'House', 'Hostel']

    # Search query
    search_query = request.GET.get('search', '').strip()
    if search_query:
        properties = properties.filter(
            Q(property_name__icontains=search_query) |
            Q(city__name__icontains=search_query) |
            Q(state__name__icontains=search_query) |
            Q(property_type__icontains=search_query) |
            Q(category__category_name__icontains=search_query)
        )

    # Filter sidebar parameters
    country_id = request.GET.get('country')
    state_id = request.GET.get('state')
    city_id = request.GET.get('city')
    category_id = request.GET.get('category')
    prop_type = request.GET.get('property_type')
    min_rent = request.GET.get('min_rent')
    max_rent = request.GET.get('max_rent')
    available_rooms = request.GET.get('available_rooms')
    rating_filter = request.GET.get('rating')

    if country_id:
        properties = properties.filter(country_id=country_id)
    if state_id:
        properties = properties.filter(state_id=state_id)
    if city_id:
        properties = properties.filter(city_id=city_id)
    if category_id:
        properties = properties.filter(category_id=category_id)
    if prop_type:
        properties = properties.filter(property_type=prop_type)
    if min_rent:
        try:
            properties = properties.filter(rent_per_month__gte=int(min_rent))
        except ValueError:
            pass
    if max_rent:
        try:
            properties = properties.filter(rent_per_month__lte=int(max_rent))
        except ValueError:
            pass
    if available_rooms:
        try:
            properties = properties.filter(available_rooms__gte=int(available_rooms))
        except ValueError:
            pass
    if rating_filter:
        try:
            # Filter properties whose average rating matches/exceeds the select option
            properties = properties.filter(avg_rating__gte=float(rating_filter))
        except ValueError:
            pass

    # Sorting
    sort_by = request.GET.get('sort_by', 'newest')
    if sort_by == 'newest':
        properties = properties.order_by('-created_at')
    elif sort_by == 'oldest':
        properties = properties.order_by('created_at')
    elif sort_by == 'rent_asc':
        properties = properties.order_by('rent_per_month')
    elif sort_by == 'rent_desc':
        properties = properties.order_by('-rent_per_month')
    elif sort_by == 'rating_desc':
        properties = properties.order_by('-avg_rating')

    # Count before pagination
    total_found = properties.count()

    # Pagination: 12 properties per page
    paginator = Paginator(properties, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get wishlisted properties for current user to render fill-hearts
    wishlisted_ids = []
    if request.user.is_authenticated:
        wishlisted_ids = Wishlist.objects.filter(user=request.user).values_list('property_id', flat=True)

    # Prepare URL parameters without page
    query = request.GET.copy()
    if 'page' in query:
        del query['page']
    url_params = query.urlencode()

    context = {
        'page_obj': page_obj,
        'countries': countries,
        'states': states,
        'cities': cities,
        'categories': categories,
        'property_types': property_types,
        'total_found': total_found,
        'wishlisted_ids': wishlisted_ids,
        'query_params': request.GET.copy(),
        'url_params': url_params,
    }
    return render(request, 'properties/properties.html', context)



# Property Detail View
def property_detail(request, pk):
    property_obj = get_object_or_404(
        Property.objects.annotate(avg_rating=Avg('reviews__rating')),
        pk=pk
    )
    
    gallery_images = property_obj.images.all()
    reviews = property_obj.reviews.all().order_by('-created_at')
    
    # Calculate star range for rating display
    avg_stars_full = 0
    avg_stars_half = False
    if property_obj.avg_rating:
        avg_stars_full = int(property_obj.avg_rating)
        avg_stars_half = (property_obj.avg_rating - avg_stars_full) >= 0.5

    # Check wishlist status
    is_wishlisted = False
    if request.user.is_authenticated:
        is_wishlisted = Wishlist.objects.filter(user=request.user, property=property_obj).exists()

    # Check if this tenant has an active pending/approved booking request for this property
    has_active_booking = False
    if request.user.is_authenticated and request.user.role == 'Tenant':
        has_active_booking = BookingRequest.objects.filter(
            tenant=request.user, 
            property=property_obj,
            status__in=['Pending', 'Approved']
        ).exists()

    # Check if user has reviewed already to block duplicates
    has_reviewed = False
    if request.user.is_authenticated:
        has_reviewed = Review.objects.filter(user=request.user, property=property_obj).exists()

    import datetime
    today_str = datetime.date.today().strftime('%Y-%m-%d')

    context = {
        'property': property_obj,
        'gallery_images': gallery_images,
        'reviews': reviews,
        'avg_stars_full': range(avg_stars_full),
        'avg_stars_empty': range(5 - avg_stars_full - (1 if avg_stars_half else 0)),
        'avg_stars_half': avg_stars_half,
        'is_wishlisted': is_wishlisted,
        'has_active_booking': has_active_booking,
        'has_reviewed': has_reviewed,
        'today_str': today_str,
    }
    return render(request, 'properties/property_detail.html', context)



# Property Management (Owner CRUD)
PropertyImageFormSet = inlineformset_factory(
    Property, PropertyImages, form=PropertyImageForm, extra=5, can_delete=True
)

@login_required
def add_property(request):
    if request.user.role != 'Owner':
        messages.error(request, "Access Denied. Only owners can list properties.")
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        formset = PropertyImageFormSet(request.POST, request.FILES)
        if form.is_valid():
            new_property = form.save(commit=False)
            new_property.owner = request.user
            new_property.save()
            
            # Save gallery images
            formset.instance = new_property
            if formset.is_valid():
                formset.save()
                messages.success(request, f"Property '{new_property.property_name}' has been successfully listed!")
                return redirect('owner_dashboard')
            else:
                messages.warning(request, "Property created, but there was an issue saving gallery images.")
                return redirect('owner_dashboard')
        else:
            messages.error(request, "Failed to create listing. Please check the details.")
    else:
        form = PropertyForm()
        formset = PropertyImageFormSet()

    return render(request, 'properties/property_form.html', {
        'form': form,
        'formset': formset,
        'action_name': 'Add New Property'
    })


@login_required
def edit_property(request, pk):
    property_obj = get_object_or_404(Property, pk=pk)
    
    if property_obj.owner != request.user:
        messages.error(request, "Access Denied. You do not own this listing.")
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=property_obj)
        formset = PropertyImageFormSet(request.POST, request.FILES, instance=property_obj)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, f"Property '{property_obj.property_name}' has been updated!")
            return redirect('owner_dashboard')
        else:
            messages.error(request, "Failed to update listing. Please correct the errors.")
    else:
        form = PropertyForm(instance=property_obj)
        formset = PropertyImageFormSet(instance=property_obj)

    return render(request, 'properties/property_form.html', {
        'form': form,
        'formset': formset,
        'action_name': f'Edit Property: {property_obj.property_name}'
    })


@login_required
def delete_property(request, pk):
    property_obj = get_object_or_404(Property, pk=pk)
    
    if property_obj.owner != request.user:
        messages.error(request, "Access Denied. You do not own this listing.")
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        title = property_obj.property_name
        property_obj.delete()
        messages.success(request, f"Property '{title}' has been successfully deleted.")
        return redirect('owner_dashboard')
        
    return render(request, 'properties/property_confirm_delete.html', {'property': property_obj})
