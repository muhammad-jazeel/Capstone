from django.urls import path
from .views import *

urlpatterns = [
    path('', homepage, name='homepage'),
    path('vendor/<int:vendor_id>/', vendor_details, name='vendor_details'),
    path('booking/<int:service_id>/', customer_booking, name='customer_booking'),
    path('customer-dashboard', customer_dashboard_view, name='customer_dashboard'),
    path('bookings/', customer_bookings_view, name='customer_bookings'),
    path('orders/', customer_orders_view, name='customer_orders'),
]
