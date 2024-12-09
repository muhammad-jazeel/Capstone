from datetime import date
import random
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from customer.utils import get_random_recommendations
from order.models import Order
from reservation.models import Reservation
from user.models import Vendor
from service.models import Service
from django.db.models import Q
from product.models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.timezone import now

def homepage(request):
    business_name = request.GET.get('business_name', '').strip()
    city = request.GET.get('city', '').strip()
    service_type = request.GET.get('service_type', '').strip()

    vendors = Vendor.objects.filter(verification_status="approved")

    if business_name:
        vendors = vendors.filter(business_name__icontains=business_name)
    if city:
        vendors = vendors.filter(address__icontains=city)
    if service_type:
        services = Service.objects.filter(name__icontains=service_type, status="active")
        vendor_ids = services.values_list('user', flat=True)
        vendors = vendors.filter(user__id__in=vendor_ids)

    context = {
        'vendors': vendors,
        'business_name': business_name,
        'city': city,
        'service_type': service_type,
    }

    return render(request, 'customer/homepage.html', context)

def vendor_details(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id, verification_status="approved")
    services = Service.objects.filter(user=vendor.user, status="active")
    products = Product.objects.filter(vendor=vendor.user, category__status='active')  
    store_images = vendor.user.store_images.all()

    context = {
        'vendor': vendor,
        'services': services,
        'products': products,
        'store_images': store_images,
    }
    return render(request, 'customer/vendor_details.html', context)

def customer_booking(request, service_id):
    service = get_object_or_404(Service, id=service_id, status="active")

    time_slots = service.time_slots.all()

    return render(request, 'customer/customer_booking.html', {'service': service, 'time_slots': time_slots})

@login_required
def customer_bookings_view(request):
    if request.user.user_type != 'customer':
        return redirect('login')

    bookings = Reservation.objects.filter(customer=request.user).select_related(
        'service', 'service__user', 'service__user__vendor'
    ).order_by('-service_date')

    search_query = request.GET.get('search', '')
    date_filter = request.GET.get('date', '')

    if search_query:
        bookings = bookings.filter(
            Q(service__name__icontains=search_query) |
            Q(service__user__vendor__business_name__icontains=search_query)
        )

    if date_filter:
        bookings = bookings.filter(service_date=date_filter)

    return render(request, 'customer/profile/customer_bookings_view.html', {
        'bookings': bookings,
        'search_query': search_query,  
        'date_filter': date_filter,  
    })


def vndrdtls(request):
    return render(request, 'customer/vendordtls.html')

def customer_booking_view(request):
    return render(request, 'customer/customer_booking.html')

def get_service_types(request):
    service_types = Service.objects.filter(status="active").values_list('name', flat=True)
    return JsonResponse(list(service_types), safe=False)

def get_suggestions(request):
    query = request.GET.get('query', '').strip()  

    if not query:
        return JsonResponse([], safe=False)  

    vendor_matches = Vendor.objects.filter(
        Q(business_name__icontains=query) | Q(description__icontains=query),
        verification_status="approved"
    ).values_list('business_name', flat=True)

    service_matches = Service.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query),
        status="active"
    ).values_list('name', flat=True)

    suggestions = list(set(vendor_matches) | set(service_matches))

    return JsonResponse(suggestions, safe=False)

@login_required(login_url='login')
def customer_dashboard_view(request):
    if request.user.user_type != 'customer':
        messages.error(request, "You are not authorized to access this page.")
        return redirect('homepage')


    upcoming_date = Reservation.objects.filter(
        customer=request.user,
        service_date__gte=date.today()
    ).values_list('service_date', flat=True).order_by('service_date').first()

    upcoming_bookings = Reservation.objects.filter(
        customer=request.user,
        service_date=upcoming_date
    ).select_related('service', 'service__user', 'service__user__vendor') if upcoming_date else []


    upcoming_pickup_date = Order.objects.filter(
        customer=request.user,
        pickup_date__gte=now().date()
    ).values_list('pickup_date', flat=True).order_by('pickup_date').first()

    upcoming_pickups = Order.objects.filter(
        customer=request.user,
        pickup_date=upcoming_pickup_date
    ).select_related('product', 'vendor') if upcoming_pickup_date else []


    recommended_services = Service.objects.filter(
        status='active',
        user__vendor__verification_status='approved'  
    ).exclude(
        user=request.user
    ).order_by('?')[:4]  

    return render(request, 'customer/profile/customer_dashboard.html', {
        'upcoming_bookings': upcoming_bookings,
        'upcoming_pickups': upcoming_pickups,
        'recommended_services': recommended_services,
    })

@login_required(login_url='login')
def customer_orders_view(request):
    if request.user.user_type != 'customer':
        messages.error(request, "You are not authorized to access this page.")
        return redirect('homepage')

    search_query = request.GET.get('search', '').strip()
    date_filter = request.GET.get('date')

    orders = Order.objects.filter(customer=request.user)

    if search_query:
        orders = orders.filter(
            product__name__icontains=search_query
        ) | orders.filter(vendor__business_name__icontains=search_query)

    if date_filter:
        orders = orders.filter(pickup_date=date_filter)

    orders = orders.order_by('-pickup_date')

    return render(request, 'customer/profile/customer_orders.html', {
        'orders': orders,
        'search_query': search_query,
        'date_filter': date_filter,
    })


