from django.urls import path
from . import views

urlpatterns = [
    path('', views.wishlist_view, name='my_wishlist'),
    path('toggle/<int:property_id>/', views.toggle_wishlist, name='toggle_wishlist'),
]
