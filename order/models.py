from django.db import models
from user.models import Account
from product.models import Product
from user.models import *

class Order(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('picked_up', 'Picked Up'),
        ('cancelled', 'Cancelled'),
    ]

    customer = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="orders",
        limit_choices_to={'user_type': 'customer'}
    )
    vendor = models.ForeignKey(
        Vendor, on_delete=models.CASCADE, related_name="orders", null=True
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="orders", null=True
    )
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    pickup_date = models.DateField(null=True)
    pickup_time = models.TimeField(null=True)
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    order_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} by {self.customer.email}"


    def is_past_pickup(self):
        """
        Check if the scheduled pickup date and time have passed.
        """
        now = timezone.now()
        scheduled_pickup = timezone.datetime.combine(self.pickup_date, self.pickup_time)
        return now > timezone.make_aware(scheduled_pickup)

    def calculate_total_price(self):
        """
        Calculate the total price of the order based on quantity and product price.
        """
        if self.product:
            return self.quantity * self.product.price
        return 0


