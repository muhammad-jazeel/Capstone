from django.urls import path
from .views import *

urlpatterns = [
    path('book/<int:service_id>/', customer_booking, name='customer_booking'),
    path('booking-confirmation/<int:reservation_id>/', booking_confirmation_view, name='booking_confirmation'),
    path('reservation/<int:reservation_id>/complete/', update_reservation_status, name='update_reservation_status'),
    path('bookings/', vendor_bookings, name='vendor_bookings'),
]
