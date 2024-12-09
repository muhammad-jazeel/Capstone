from django.db import models
from service.models import Service
from department.models import *
from user.models import Account

class Staff(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="staff", null=True)  
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    image = models.ImageField(upload_to='staff_images/', null=True, blank=True)  
    departments = models.ManyToManyField(Department, related_name="staff")  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class StaffServiceAssignment(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.staff.first_name} {self.staff.last_name} - {self.service.name}"