from django.urls import path
from . import views

urlpatterns = [
    path('', views.payment_list, name='payment_list'),
    path('record/', views.record_payment, name='record_payment'),
]
