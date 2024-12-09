from django.db import models
from user.models import Account
from reservation.models import Reservation
from order.models import Order

class Payment(models.Model):
    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE, related_name='payment', null=True)
    customer = models.ForeignKey(Account, on_delete=models.CASCADE)
    stripe_charge_id = models.CharField(max_length=100, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=10.00)  # Default $10 booking fee
    refunded = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.stripe_charge_id} - {self.customer.email}"
