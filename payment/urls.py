from django.urls import path
from .views import *

urlpatterns = [
    path('checkout-session/<int:reservation_id>/', create_checkout_session, name='create_checkout_session'),
    path('payment-success/', payment_success, name='payment_success'),
]
