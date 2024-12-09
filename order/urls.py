from django.urls import path
from .views import *

urlpatterns = [
    path('store-pickup/<int:product_id>/', store_pickup_view, name='store_pickup'),
    path('confirm-pickup/<int:product_id>/', confirm_pickup, name='order_confirm_pickup'),
    path("confirmation/<int:order_id>/", order_confirmation, name="order_confirmation"),
    path('orders/', vendor_orders, name='vendor_orders'),
]
