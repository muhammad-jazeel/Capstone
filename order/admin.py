from django.contrib import admin
from .models import *

# Register your models here.

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('customer', 'vendor', 'product', 'pickup_date', 'pickup_time', 'status', 'total_price')
    list_filter = ('status', 'pickup_date', 'vendor')
    search_fields = ('customer__email', 'vendor__business_name', 'product__name')

