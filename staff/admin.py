from django.contrib import admin
from .models import *

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone_number')

@admin.register(StaffServiceAssignment)
class StaffServieAssignmentAdmin(admin.ModelAdmin):
    list_display = ('staff', 'service', 'assigned_at')


