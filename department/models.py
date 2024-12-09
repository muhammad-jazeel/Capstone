from django.db import models
from user.models import Account

class Department(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    name = models.CharField(max_length=100, unique=True)
    created_by = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="departments", null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def set_inactive(self):
        """Set the department and its services to inactive."""
        self.status = 'inactive'
        self.save()
        self.services.update(status='inactive')

