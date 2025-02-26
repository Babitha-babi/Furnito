from django.db import models
from userauths.models import CustomUser
from core.models import Product  # Assuming you have a Product model

class Wishlist(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')  # To prevent adding the same product multiple times.

    def __str__(self):
        return f"{self.user.username}'s Wishlist"




