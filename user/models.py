from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.db import models
import random

class MyAccountManager(BaseUserManager):
    def create_user(self, first_name, last_name, email, phone_number, password=None, user_type=None):
        if not email:
            raise ValueError('User must have an email address')
        if not phone_number:
            raise ValueError('User must have a phone number')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            user_type=user_type
        )
        user.set_password(password)

        if user_type == 'customer':
            user.is_customer = True
        elif user_type == 'vendor':
            user.is_vendor = True

        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, email, phone_number, password):
        user = self.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            password=password,
            user_type='admin'
        )
        user.is_vendor = True
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save(using=self._db)
        return user

class Account(AbstractUser):
    USER_TYPES = [
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
        ('admin', 'Admin'),
    ]
    username = None
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPES)

    # New fields
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)  # New city field
    postal_code = models.CharField(max_length=20, blank=True, null=True)  # New postal code field
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)  # Profile image

    is_customer = models.BooleanField(default=False)
    is_vendor = models.BooleanField(default=False)

    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    otp_code = models.CharField(max_length=6, blank=True, null=True)
    is_otp_verified = models.BooleanField(default=False)
    otp_generated_at = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number']

    objects = MyAccountManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return True
    
    def generate_otp(self):
        """Generate a random 6-digit OTP, set generation time, and save it."""
        import random
        self.otp_code = f"{random.randint(100000, 999999)}"
        self.otp_generated_at = timezone.now()
        self.save()

    def is_otp_expired(self):
        """Check if the OTP is expired."""
        if self.otp_generated_at:
            expiration_time = self.otp_generated_at + timedelta(minutes=5)  # OTP valid for 5 minutes
            return timezone.now() > expiration_time
        return True  # If `otp_generated_at` is not set, consider it expired
    
    def verify_otp(self, otp):
        """Verify the given OTP."""
        return self.otp_code == otp

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='accounts',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='accounts',
        blank=True,
    )

class Vendor(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=255)
    business_license = models.CharField(max_length=255, null=True, blank=True)  # Business license
    business_email = models.EmailField(max_length=255, null=True, blank=True)  # Business email
    business_contact = models.CharField(max_length=15, null=True, blank=True)  # Business contact
    address = models.TextField(null=True, blank=True)  # Full address
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    description = models.TextField(null=True, blank=True)  # Business description
    verification_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected')
        ],
        default='pending'
    ) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.business_name

class StoreImage(models.Model):
    vendor = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='store_images')
    image = models.ImageField(upload_to='store_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.vendor.email}"