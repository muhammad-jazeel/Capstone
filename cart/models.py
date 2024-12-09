from django.db import models
from user.models import Account
from product.models import Product

class Cart(models.Model):
    customer = models.ForeignKey(Account, on_delete=models.CASCADE, limit_choices_to={'user_type': 'customer'})
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)  # This flag ensures you have only one active cart at a time for a user.

    def __str__(self):
        return f"Cart {self.id} for {self.customer.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} of {self.product.name} in Cart {self.cart.id}"

    def get_total_price(self):
        return self.product.price * self.quantity


