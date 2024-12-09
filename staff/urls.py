from django.urls import path
from .views import *

urlpatterns = [
    path('', staffs_view, name='staffs'),
    path('addstaff/', add_staff_view, name='add_staff'),
    path('editstaff/<int:staff_id>/', edit_staff_view, name='edit_staff'),
    path('deletestaff/<int:staff_id>/', delete_staff_view, name='delete_staff'),
]
