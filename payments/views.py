from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import RentPayment
from .forms import RentPaymentForm
from bookings.models import BookingRequest

@login_required
def payment_list(request):
    form = None
    if request.user.role == 'Owner':
        # Get payments for properties owned by this owner
        payments = RentPayment.objects.filter(property__owner=request.user).order_by('-payment_date')
    else:
        # Get payments made by this tenant
        payments = RentPayment.objects.filter(user=request.user).order_by('-payment_date')
        
        # Instantiate form only for tenants
        form = RentPaymentForm(user=request.user)
        
        # Check if tenant has any approved bookings
        has_approved_bookings = BookingRequest.objects.filter(
            tenant=request.user,
            status='Approved'
        ).exists()
        
    context = {
        'payments': payments,
        'form': form,
        'has_approved_bookings': has_approved_bookings if request.user.role == 'Tenant' else False
    }
    return render(request, 'payments/payment_list.html', context)


@login_required
def record_payment(request):
    if request.user.role != 'Tenant':
        messages.error(request, "Access Denied. Only tenants can record payments.")
        return redirect('payment_list')

    if request.method == 'POST':
        form = RentPaymentForm(request.POST, user=request.user)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.user = request.user
            payment.save()
            messages.success(request, f"Payment of {payment.amount} for {payment.property.property_name} recorded as {payment.status}!")
            return redirect('payment_list')
        else:
            messages.error(request, "Failed to record payment. Please correct the form errors.")
            
            # Re-render the list page with the error form
            payments = RentPayment.objects.filter(user=request.user).order_by('-payment_date')
            context = {
                'payments': payments,
                'form': form,
                'has_approved_bookings': True
            }
            return render(request, 'payments/payment_list.html', context)

    return redirect('payment_list')
