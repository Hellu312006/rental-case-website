from django.urls import path
from . import views

urlpatterns = [
    path('request/<int:property_id>/', views.create_booking, name='create_booking'),
    path('action/<int:booking_id>/<str:action>/', views.booking_action, name='booking_action'),
]
