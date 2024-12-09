from django.utils.timezone import localtime, now
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from order.models import Order
from reservation.models import Reservation
from service.models import Service
from staff.models import Staff
from department.models import Department

@login_required
def dashboard_view(request):
    if request.user.user_type != 'vendor':
        messages.error(request, "You do not have permission to access the vendor dashboard.")
        return redirect('home')

    total_services = Service.objects.filter(user=request.user).count()
    total_staff = Staff.objects.filter(user=request.user).count()
    total_bookings = Reservation.objects.filter(vendor=request.user).count()  
    active_departments = Department.objects.filter(
        created_by=request.user, status='active'
    ).count()

    today = localtime(now()).date()

    vendor_services = Service.objects.filter(user=request.user)

    today_reservations = Reservation.objects.filter(
        service__in=vendor_services,
        service_date=today
    ).select_related('customer', 'service', 'time_slot')

    todays_pickups = Order.objects.filter(
        vendor__user=request.user,
        pickup_date=today
    ).select_related('customer', 'product', 'vendor')

    return render(request, 'vendor/dashboard.html', {
        'total_services': total_services,
        'total_staff': total_staff,
        'active_departments': active_departments,
        'total_bookings': total_bookings,  
        'vendor_reservations': today_reservations, 
        'todays_pickups': todays_pickups,
        'today': today, 
    })



