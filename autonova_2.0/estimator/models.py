from django.db import models

class SparePart(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    vehicle_type = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.name} - ₹{self.price}"