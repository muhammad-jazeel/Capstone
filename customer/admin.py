from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone_number', 'address', 'profile_completed', 'created_at')
    list_filter = ('profile_completed', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone_number')
