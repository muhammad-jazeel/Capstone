from datetime import date
from time import localtime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import check_password
from django.contrib.auth import update_session_auth_hash
from customer.models import Customer
from department.models import Department
from reservation.models import Reservation
from service.models import Service
from staff.models import Staff
from .serializers import *
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .utils import *
from .models import *
from django.utils.timezone import now

def signup(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        re_password = request.POST.get('repassword')
        user_type = request.POST.get('user_type')

        if password != re_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'auth/signup.html')

        if Account.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, 'auth/signup.html')

        if Account.objects.filter(phone_number=phone_number).exists():
            messages.error(request, "Phone number already registered.")
            return render(request, 'auth/signup.html')

        try:
            # Create the user
            user = Account.objects.create_user(
                email=email,
                phone_number=phone_number,
                password=password,
                first_name='',
                last_name='',
                user_type=user_type
            )
            # Generate OTP and send it
            user.generate_otp()
            send_otp_email(user)
            messages.success(request, "Account created successfully. Please verify your email via OTP.")
            auth_login(request, user)  # Log the user in after signup
            return redirect('verify_otp')  # Redirect to OTP verification page
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return render(request, 'auth/signup.html')

    return render(request, 'auth/signup.html')

def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            if not user.is_otp_verified:
                auth_login(request, user)  # Log in the user to allow access to OTP verification
                messages.warning(request, "Please verify your email via OTP before accessing the dashboard.")
                return redirect('verify_otp')  # Redirect to OTP verification page
            
            # If OTP is verified, proceed to the dashboard
            auth_login(request, user)
            if user.user_type == 'vendor':
                return redirect('dashboard')
            elif user.user_type == 'customer':
                return redirect('homepage')
            else:
                messages.error(request, "Invalid user type.")
                return redirect('login')
        else:
            messages.error(request, "Invalid email or password.")
            return render(request, 'auth/login.html')

    return render(request, 'auth/login.html')

def logout(request):
    auth_logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('login')

@api_view(['GET'])
def get_user(request, user_id):
    try:
        user = Account.objects.get(pk=user_id)
    except Account.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = AccountSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_all_users(request):
    users = Account.objects.all()
    serializer = AccountSerializer(users, many=True)  
    return Response(serializer.data, status=200)

@login_required
def dashboard_view(request):
    # Ensure the user is a vendor
    if request.user.user_type != 'vendor':
        messages.error(request, "You do not have permission to access the vendor dashboard.")
        return redirect('home')

    # Fetch reservations
    # vendor_bookings = Reservation.objects.filter(
    #     vendor=request.user
    # ).select_related('customer', 'service', 'time_slot')

    

    vendor_reservations = Reservation.objects.all()
    print("Hello")

    # Debugging
    print(f"Vendor Bookings: {vendor_reservations}")
    for booking in vendor_reservations:
        print(f"ID: {booking.id}, Customer: {booking.customer}, Service: {booking.service.name}")

    return render(request, 'vendor/dashboard.html', {
        'vendor_reservations': vendor_reservations,
    })


def generate_otp_view(request):
    user = request.user

    if request.method == 'POST':
        user.generate_otp()  # Regenerate OTP
        send_otp_email(user)  # Resend OTP via email
        messages.success(request, "A new OTP has been sent to your email.")
        return redirect('verify_otp')

    # For GET requests, simply display the generate OTP page
    return render(request, 'auth/generate_otp.html', {'email': user.email})

def verify_otp_view(request):
    if not request.user.is_authenticated:
        messages.error(request, "You need to log in to verify OTP.")
        return redirect('login')

    user = request.user

    if request.method == 'POST':
        otp = request.POST.get('otp')

        if user.verify_otp(otp):
            if not user.is_otp_expired():
                user.is_otp_verified = True
                user.save()
                messages.success(request, "OTP verified successfully.")

                # Redirect based on user type
                if user.user_type == 'customer':
                    # Redirect to customer profile creation if not completed
                    if not hasattr(user, 'customer') or not user.customer.profile_completed:
                        return redirect('add_customer_profile')
                    return redirect('homepage')
                elif user.user_type == 'vendor':
                    return redirect('vendor_profile')
                else:
                    messages.error(request, "Invalid user type.")
                    return redirect('login')
            else:
                messages.error(request, "The OTP has expired. Please request a new one.")
                return redirect('generate_otp')
        else:
            messages.error(request, "Invalid OTP.")

    return render(request, 'auth/otp_verification.html', {'email': user.email})

@login_required
def add_customer_profile(request):
    if request.method == 'POST':
        # Get form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        address = request.POST.get('address')
        city = request.POST.get('city')
        postal_code = request.POST.get('postal_code')
        profile_image = request.FILES.get('profile_image')  # Handle file upload

        # Update the logged-in user's profile
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.address = address
        user.city = city
        user.postal_code = postal_code
        if profile_image:
            user.profile_image = profile_image  # Save profile image if uploaded
        user.save()

        messages.success(request, "Profile updated successfully!")
        return redirect('customer_dashboard')  # Redirect to the dashboard or any desired page

    return render(request, 'customer/customer_profile.html')


def vendor_profile_view(request):
    if request.method == "POST":
        business_name = request.POST.get("business_name")
        address = request.POST.get("address")
        latitude, longitude = geocode_address(address)

        if latitude and longitude:
            Vendor.objects.update_or_create(
                user=request.user,
                defaults={
                    "business_name": business_name,
                    "address": address,
                    "latitude": latitude,
                    "longitude": longitude,
                },
            )
            messages.success(request, "Profile saved successfully!")
            return redirect("vendor_dashboard")
        else:
            messages.error(request, "Invalid address. Please try again.")

    return render(request, "vendor/profile.html")

def create_profile_view(request):
    if request.method == 'POST':
        business_name = request.POST.get('business_name')
        business_email = request.POST.get('business_email')
        business_contact = request.POST.get('business_contact')
        business_license = request.POST.get('business_license')
        street = request.POST.get('street')
        city = request.POST.get('city')
        province = request.POST.get('province')
        postal_code = request.POST.get('postal_code')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        description = request.POST.get('description')

        # Combine street, city, province, and postal code into one address
        address = f"{street}, {city}, {province}, {postal_code}"

        # Create or update the vendor profile
        vendor, created = Vendor.objects.update_or_create(
            user=request.user,
            defaults={
                'business_name': business_name,
                'business_email': business_email,
                'business_contact': business_contact,
                'business_license' : business_license,
                'address': address,
                'latitude': latitude if latitude else None,
                'longitude': longitude if longitude else None,
                'description': description,
            },
        )

        if created:
            messages.success(request, "Profile created successfully.")
        else:
            messages.success(request, "Profile updated successfully.")
        
        return redirect('dashboard')  # Redirect to dashboard or another page
    
    return render(request, 'vendor/create_profile.html')

@login_required
def profile_view(request):
    # Get the vendor's profile
    try:
        vendor = Vendor.objects.get(user=request.user)
    except Vendor.DoesNotExist:
        vendor = None  # Handle gracefully if no vendor is found

    # Get the store images associated with the logged-in user (Account)
    store_images = StoreImage.objects.filter(vendor=request.user)

    context = {
        'vendor': vendor,
        'store_images': store_images,
    }
    return render(request, 'vendor/profile_view.html', context)

@login_required
def customer_profile_view(request):
    return render(request, 'customer/profile/customer_profile_view.html', {'user': request.user})

@login_required
def update_personal_details(request):
    if request.method == 'POST':
        user = request.user
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        city = request.POST.get('city')
        postal_code = request.POST.get('postal_code')

        # Check if the phone number already exists for another user
        if Account.objects.filter(phone_number=phone_number).exclude(id=user.id).exists():
            error_message = "This phone number is already registered with another account."
            return render(request, 'customer/profile/customer_profile_view.html', {
                'user': user,
                'error_message': error_message
            })

        # Update user fields
        user.first_name = first_name
        user.last_name = last_name
        user.phone_number = phone_number
        user.address = address
        user.city = city
        user.postal_code = postal_code

        # Handle profile image upload
        if 'profile_image' in request.FILES:
            user.profile_image = request.FILES['profile_image']

        user.save()
        messages.success(request, "Personal details updated successfully!")
        return redirect('customer_profile_view')

    return redirect('customer_profile_view')

# @login_required
# def update_password(request):
#     if request.method == 'POST':
#         user = request.user
#         old_password = request.POST.get('old_password')
#         new_password = request.POST.get('new_password')
#         confirm_password = request.POST.get('confirm_password')

#         if not check_password(old_password, user.password):
#             return render(request, 'customer/profile/customer_profile_view.html', {
#                 'error_message_pass': "The old password is incorrect."
#             })

#         if new_password != confirm_password:
#             return render(request, 'customer/profile/customer_profile_view.html', {
#                 'error_message_pass': "The new passwords do not match."
#             })

#         user.set_password(new_password)
#         user.save()
#         update_session_auth_hash(request, user)
#         messages.success(request, "Password updated successfully!")
#         return redirect('customer_profile_view')

#     return redirect('customer_profile_view')

@login_required
def update_password(request):
    if request.method == 'POST':
        user = request.user
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Check if the old password matches the stored password
        if not user.check_password(old_password):  # Use `user.check_password` instead of `check_password`
            messages.error(request, "The old password is incorrect.")
            return redirect('customer_profile_view' if user.is_customer else 'profile_view')

        # Validate new password and confirm password
        if new_password != confirm_password:
            messages.error(request, "The new passwords do not match.")
            return redirect('customer_profile_view' if user.is_customer else 'profile_view')

        # Validate password strength (optional)
        if len(new_password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return redirect('customer_profile_view' if user.is_customer else 'profile_view')

        # Save the new password
        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user)  # Keeps the user logged in
        messages.success(request, "Password updated successfully!")

        # Redirect based on user type
        if user.is_customer:
            return redirect('customer_profile_view')
        elif user.is_vendor:
            return redirect('profile_view')
        else:
            return redirect('dashboard')

    # Default redirect for GET requests
    return redirect('customer_profile_view' if request.user.is_customer else 'profile_view')

@login_required
def update_vendor_password(request):
    if request.method == 'POST':
        user = request.user
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Ensure the user is a vendor
        if not hasattr(user, 'vendor'):
            messages.error(request, "You do not have permission to perform this action.")
            return redirect('dashboard')

        if not check_password(old_password, user.password):
            return render(request, 'vendor/profile_view.html', {  # Explicit path
                'error_message_pass': "The old password is incorrect."
            })

        if new_password != confirm_password:
            return render(request, 'vendor/profile_view.html', {  # Explicit path
                'error_message_pass': "The new passwords do not match."
            })

        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user)
        messages.success(request, "Password updated successfully!")
        return redirect('profile_view')

    return redirect('profile_view')

@login_required
def upload_image(request):
    if request.method == 'POST':
        image = request.FILES.get('image')
        if image:
            StoreImage.objects.create(vendor=request.user, image=image)
            messages.success(request, "Image uploaded successfully.")
        else:
            messages.error(request, "Failed to upload image. Please try again.")
    return redirect('profile_view')

@login_required
def remove_image(request, image_id):
    image = get_object_or_404(StoreImage, id=image_id, vendor=request.user)
    image.delete()
    messages.success(request, "Image removed successfully.")
    return redirect('profile_view')

def new_profile(request):
    return render(request, 'vendor/newprofile.html')


