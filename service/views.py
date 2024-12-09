from datetime import date, datetime, time, timedelta
import logging
from venv import logger
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Service, Department, TimeSlot
from staff.models import *
from .forms import ServiceForm  
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_time

logger = logging.getLogger('custom_logger')

@login_required
def add_services_view(request):
    if request.method == 'POST':
        name = request.POST.get('serviceName')
        price = request.POST.get('servicePrice')
        duration_minutes = request.POST.get('serviceDuration')
        start_time = request.POST.get('startTime')  
        end_time = request.POST.get('endTime')  
        description = request.POST.get('serviceDescription')
        selected_staff_ids = request.POST.getlist('selectedStaffs')
        image = request.FILES.get('image')  

        if not all([name, price, duration_minutes, start_time, end_time, description]):
            messages.error(request, "All fields are required except 'Staff Assigned'.")
            return redirect('add_services_view')

        try:
            start_time = datetime.strptime(start_time, "%H:%M").time()
            end_time = datetime.strptime(end_time, "%H:%M").time()

            with transaction.atomic():
                service = Service.objects.create(
                    name=name,
                    description=description,
                    price=float(price),  
                    duration_minutes=int(duration_minutes),  
                    start_time=start_time,
                    end_time=end_time,
                    user=request.user,
                    image=image  
                )

                current_time = start_time
                delta = timedelta(minutes=int(duration_minutes))
                while current_time < end_time:
                    TimeSlot.objects.create(service=service, time=current_time)
                    current_time = (datetime.combine(date.today(), current_time) + delta).time()

                logger.info(f"Service created with time slots.")

                for staff_id in selected_staff_ids:
                    staff = Staff.objects.filter(id=staff_id, user=request.user).first()
                    if staff:
                        StaffServiceAssignment.objects.create(service=service, staff=staff)

                messages.success(request, f"Service '{service.name}' added successfully!")
                return redirect('services')

        except Exception as e:
            logger.error(f"Error adding service: {str(e)}")
            messages.error(request, f"Error adding service: {str(e)}")
            return redirect('add_services_view')

    staffs = Staff.objects.filter(user=request.user)
    return render(request, 'vendor/service/add_services.html', {'staffs': staffs})


@login_required
def edit_service_view(request, service_id):
    service = get_object_or_404(Service, id=service_id, user=request.user)

    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        duration_minutes = request.POST.get('duration_minutes')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        description = request.POST.get('description')
        status = request.POST.get('status')
        selected_staff_ids = request.POST.getlist('staffs')
        new_image = request.FILES.get('image')  

        try:
            service.name = name
            service.price = float(price)
            service.duration_minutes = int(duration_minutes)
            service.description = description
            service.status = status

            if start_time:
                service.start_time = datetime.strptime(start_time, "%H:%M").time()
            if end_time:
                service.end_time = datetime.strptime(end_time, "%H:%M").time()

            if new_image:
                service.image = new_image  

            service.save()

            StaffServiceAssignment.objects.filter(service=service).delete()
            for staff_id in selected_staff_ids:
                staff = Staff.objects.filter(id=staff_id, user=request.user).first()
                if staff:
                    StaffServiceAssignment.objects.create(service=service, staff=staff)

            messages.success(request, f"Service '{service.name}' updated successfully!")
            return redirect('services')

        except Exception as e:
            logger.error(f"Error updating service: {str(e)}")
            messages.error(request, f"Error updating service: {str(e)}")
            return redirect('edit_service_view', service_id=service_id)

    assigned_staff_ids = StaffServiceAssignment.objects.filter(service=service).values_list('staff_id', flat=True)
    staffs = Staff.objects.filter(user=request.user)
    slots = service.time_slots.all()

    return render(
        request,
        'vendor/service/edit_services.html',
        {
            'service': service,
            'staffs': staffs,
            'assigned_staff_ids': assigned_staff_ids,
            'slots': slots,
        }
    )

@csrf_exempt
@login_required
def update_time_slots(request, service_id):
    service = get_object_or_404(Service, id=service_id, user=request.user)

    if request.method == 'POST':
        removed_slot_ids = request.POST.getlist('removed_slots', [])

        try:
            with transaction.atomic():
                TimeSlot.objects.filter(service=service, id__in=removed_slot_ids).delete()
            return JsonResponse({'status': 'success', 'message': 'Time slots updated successfully!'})

        except Exception as e:
            logger.error(f"Error updating time slots: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})



@login_required
def delete_service_view(request, service_id):
    service = get_object_or_404(Service, id=service_id, user=request.user)
    if request.method == 'POST':
        StaffServiceAssignment.objects.filter(service=service).delete()  
        service.delete()
        messages.success(request, f"Service '{service.name}' deleted successfully!")
        return redirect('services')
    return render(request, 'vendor/service/delete_services.html', {'service': service})

@login_required
def services_view(request):
    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '').strip()  
    services = Service.objects.filter(user=request.user)

    if search_query:
        services = services.filter(name__icontains=search_query)

    if status_filter in ['active', 'inactive']:
        services = services.filter(status=status_filter)

    return render(request, 'vendor/service/services.html', {
        'services': services,
        'status_filter': status_filter  
    })


