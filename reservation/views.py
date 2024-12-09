import datetime
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
import stripe
from payment.views import create_checkout_session
from service.models import Service, TimeSlot
from .models import Reservation
import logging
from django.db.models import Q

def customer_booking(request, service_id):
    service = get_object_or_404(Service, id=service_id, status="active")

    all_time_slots = service.time_slots.all()

    reserved_time_slots = Reservation.objects.filter(
        service=service,
        service_date__gte=datetime.date.today(),  
    ).values_list('time_slot_id', flat=True)

    available_time_slots = all_time_slots.exclude(id__in=reserved_time_slots)

    if request.method == 'POST':
        time_slot_id = request.POST.get('Service_Time')
        service_date = request.POST.get('Service_Date')
        car_registration = request.POST.get('Car_Registration')
        additional_comments = request.POST.get('Additional_Comments')

        if not time_slot_id or not service_date or not car_registration:
            messages.error(request, "Please fill in all required fields.")
            return render(request, 'customer/customer_booking.html', {
                'service': service,
                'time_slots': available_time_slots,
            })

        if Reservation.objects.filter(
            service=service,
            service_date=service_date,
            time_slot_id=time_slot_id,
        ).exists():
            messages.error(request, "The selected time slot is no longer available. Please choose another.")
            return render(request, 'customer/customer_booking.html', {
                'service': service,
                'time_slots': available_time_slots,
            })

        time_slot = get_object_or_404(TimeSlot, id=time_slot_id)

        reservation = Reservation.objects.create(
            customer=request.user,
            service=service,
            time_slot=time_slot,
            service_date=service_date,
            car_registration=car_registration,
            comments=additional_comments,
            total_price=service.price,  
            status='confirmed',
        )

        messages.success(request, "Your booking has been confirmed!")
        return redirect('booking_confirmation', reservation_id=reservation.id)

    return render(request, 'customer/customer_booking.html', {
        'service': service,
        'time_slots': available_time_slots,  
    })



def booking_confirmation_view(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    context = {
        'service': reservation.service,
        'booking': {
            'car_registration': reservation.car_registration,
            'service_date': reservation.service_date,  
            'service_time': reservation.time_slot.time,
            'additional_comments': reservation.comments or "None provided",
        },
    }
    return render(request, 'customer/booking_confirmation.html', context)

@login_required
def update_reservation_status(request, reservation_id):
    if request.user.user_type != 'vendor':
        messages.error(request, "You do not have permission to update the reservation status.")
        return redirect('dashboard')

    reservation = get_object_or_404(Reservation, id=reservation_id, vendor=request.user)

    reservation.status = 'completed'
    reservation.save()
    messages.success(request, f"Reservation #{reservation.id} has been marked as completed.")

    return redirect('dashboard')

@login_required
def vendor_bookings(request):
    if request.user.user_type != 'vendor':
        messages.error(request, "You do not have permission to access this page.")
        return redirect('dashboard')

    vendor_reservations = Reservation.objects.filter(vendor=request.user).select_related('customer', 'service')

    search_query = request.GET.get('search', '')
    if search_query:
        vendor_reservations = vendor_reservations.filter(
            Q(customer__first_name__icontains=search_query) |
            Q(customer__last_name__icontains=search_query) |
            Q(car_registration__icontains=search_query) |
            Q(service__name__icontains=search_query)
        )

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        vendor_reservations = vendor_reservations.filter(service_date__range=[start_date, end_date])

    context = {
        'vendor_reservations': vendor_reservations,
        'search_query': search_query,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'vendor/bookings/all_bookings.html', context)