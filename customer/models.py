from django.db import models
from user.models import Account  

class Customer(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="customers")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)  
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)  
    profile_completed = models.BooleanField(default=False)  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
