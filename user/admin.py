from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Account)
@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'verification_status', 'created_at', 'updated_at')
    search_fields = ('business_name', 'business_license')
    list_filter = ('verification_status',)

admin.site.register(StoreImage)