from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from order.models import Order
from product.models import Product
from user.models import Vendor

# Create your views here.

def store_pickup_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    return render(request, 'customer/store_pickup.html', {
        'product': product,
    })

@login_required(login_url='login')
def confirm_pickup(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    vendor = get_object_or_404(Vendor, user=product.vendor)

    if request.method == "POST":
        quantity = int(request.POST.get("quantity", 1))
        pickup_date = request.POST.get("pickup_date")
        pickup_time = request.POST.get("pickup_time")
        notes = request.POST.get("notes", "")
        total_price = float(product.price) * quantity

        order = Order.objects.create(
            customer=request.user,  
            vendor=vendor,          
            product=product,        
            pickup_date=pickup_date,
            pickup_time=pickup_time,
            quantity=quantity,
            total_price=total_price,
            notes=notes,
            status="confirmed",
        )

        messages.success(request, "Your order has been successfully placed!")
        return redirect("order_confirmation", order_id=order.id)

    return redirect("store_pickup", product_id=product.id)

@login_required(login_url='login')
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    return render(request, "customer/order_confirmation.html", {"order": order})

@login_required
def vendor_orders(request):
    if request.user.user_type != 'vendor':
        messages.error(request, "You do not have permission to access this page.")
        return redirect('dashboard')

    vendor_orders = Order.objects.filter(vendor=request.user.vendor).select_related('customer', 'product')

    search_query = request.GET.get('search', '')
    if search_query:
        vendor_orders = vendor_orders.filter(
            Q(customer__first_name__icontains=search_query) |
            Q(customer__last_name__icontains=search_query) |
            Q(product__name__icontains=search_query)
        )

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        vendor_orders = vendor_orders.filter(pickup_date__range=[start_date, end_date])

    status_filter = request.GET.get('status', '')
    if status_filter:
        vendor_orders = vendor_orders.filter(status=status_filter)

    context = {
        'vendor_orders': vendor_orders,
        'search_query': search_query,
        'start_date': start_date,
        'end_date': end_date,
        'status_filter': status_filter,
    }
    return render(request, 'vendor/orders/orders.html', context)