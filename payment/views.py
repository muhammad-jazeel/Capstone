from django.urls import reverse
import stripe
from django.conf import settings
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_checkout_session(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f"Booking Fee for {reservation.service.name}",
                    },
                    'unit_amount': int(reservation.total_price * 100),  # Amount in cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri('/payment-success/') + f"?reservation_id={reservation.id}",
            cancel_url=request.build_absolute_uri('/payment-cancel/'),
        )
        return JsonResponse({'session_id': session.id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    
@login_required
def payment_success(request):
    reservation_id = request.GET.get('reservation_id')
    reservation = get_object_or_404(Reservation, id=reservation_id)

    # Save payment details
    Payment.objects.create(
        reservation=reservation,
        customer=request.user,
        amount=reservation.total_price,
    )

    # Update reservation status to confirmed
    reservation.status = 'confirmed'
    reservation.payment_status = 'paid'
    reservation.save()

    messages.success(request, "Payment successful! Your booking is confirmed.")
    return redirect('booking_confirmation') 


