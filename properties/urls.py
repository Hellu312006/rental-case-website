from django.urls import path
from . import views

urlpatterns = [
    path('', views.properties_list, name='properties_list'),
    path('property/<int:pk>/', views.property_detail, name='property_detail'),
    path('property/add/', views.add_property, name='add_property'),
    path('property/<int:pk>/edit/', views.edit_property, name='edit_property'),
    path('property/<int:pk>/delete/', views.delete_property, name='delete_property'),
    path('ajax/load-states/', views.load_states, name='ajax_load_states'),
    path('ajax/load-cities/', views.load_cities, name='ajax_load_cities'),
]
