from django.urls import path
from .views import *

urlpatterns = [
    path('services/add/', add_services_view, name='add_services_view'),
    path('services/edit/<int:service_id>/', edit_service_view, name='edit_service_view'),
    path('services/delete/<int:service_id>/', delete_service_view, name='delete_service_view'),
    path('', services_view, name='services'),
    path('service/<int:service_id>/update-time-slots/', update_time_slots, name='update_time_slots'),
    
]
