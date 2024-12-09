from django.db import models
from user.models import Account
from service.models import *

class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed')
    ]
    PAYMENT_STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid')
    ]

    customer = models.ForeignKey(Account, on_delete=models.CASCADE, limit_choices_to={'user_type': 'customer'})
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True)  # Linked to the booked service
    vendor = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="vendor_reservations", null=True, blank=True)  # Automatically populated
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)  # Linked to the selected time slot
    service_date = models.DateField(null=True)
    car_registration = models.CharField(max_length=50, null=True)
    comments = models.TextField(null=True, blank=True)  # Optional comments from the customer
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')  # Default set to confirmed
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Automatically set the vendor from the service's vendor
        if self.service and self.service.user:
            self.vendor = self.service.user
        super().save(*args, **kwargs)

    def __str__(self):
        customer_name = self.customer.first_name if self.customer else "None"
        return f"Reservation for {customer_name} - {self.service.name if self.service else 'No Service'}"

