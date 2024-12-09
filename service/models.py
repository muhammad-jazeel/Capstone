from django.db import models
from department.models import *
from datetime import date, datetime, timedelta
from django.db import models, transaction
from user.models import *
import json


class Service(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_minutes = models.IntegerField()
    start_time = models.TimeField(null=True)
    end_time = models.TimeField(null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="services", null=True)
    image = models.ImageField(upload_to='service_images/', null=True, blank=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="services", null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def calculate_slots(self):
        """Calculate and create TimeSlot objects based on start_time, end_time, and duration."""
        if not self.start_time or not self.end_time or not self.duration_minutes:
            return

        self.time_slots.all().delete()

        current_time = self.start_time
        delta = timedelta(minutes=self.duration_minutes)

        while current_time < self.end_time:
            TimeSlot.objects.create(service=self, time=current_time)
            current_time = (datetime.combine(date.today(), current_time) + delta).time()

    def save(self, *args, **kwargs):
        if self.pk:  
            original = Service.objects.filter(pk=self.pk).only('start_time', 'end_time').first()
            if original and (self.start_time != original.start_time or self.end_time != original.end_time):
                self.calculate_slots()

        super().save(*args, **kwargs)


class TimeSlot(models.Model):
    service = models.ForeignKey('Service', on_delete=models.CASCADE, related_name='time_slots')
    time = models.TimeField()

    def __str__(self):
        return f"{self.service.name} - {self.time}"



