from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactUsForm

def contact_view(request):
    if request.method == 'POST':
        form = ContactUsForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your message has been sent successfully! We will get back to you shortly.")
            return redirect('contact')
        else:
            messages.error(request, "Failed to send message. Please check the fields and try again.")
    else:
        form = ContactUsForm()
        
    return render(request, 'contact/contact.html', {'form': form})
