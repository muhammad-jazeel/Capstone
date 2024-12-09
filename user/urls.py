from django.urls import path
from .views import *

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', user_login, name='login'),
    path('logout/', logout, name='logout'),
    path('verify-otp/', verify_otp_view, name='verify_otp'),
    path('generate-otp/', generate_otp_view, name='generate_otp'),

    path('dashboard/', dashboard_view, name='dashboard'),

    path("profile/", vendor_profile_view, name="vendor_profile"),
    path('profile/create/', create_profile_view, name='create_profile'),
    path('newprofile/',new_profile, name="new_profile"),
    path('profile_view/', profile_view, name='profile_view'),
    path('profile/upload/', upload_image, name='upload_image'),
    path('profile/remove/<int:image_id>/', remove_image, name='remove_image'),
    path('add-profile/', add_customer_profile, name='add_customer_profile'),
    path('customer-profile/', customer_profile_view, name='customer_profile_view'),
    path('update-personal-details/', update_personal_details, name='update_personal_details'),
    path('update-password/', update_password, name='update_password'),
    path('vendor/update-password/', update_vendor_password, name='update_vendor_password'),
]
