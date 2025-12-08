from django.db import models
from datetime import date

class WishlistItem(models.Model):
    items = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.items


STORAGE_TYPES = [
    ('Room', 'Room'),
    ('Fridge', 'Fridge'),
    ('Freezer', 'Freezer'),
]

class InventoryItem(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.IntegerField(default=1)
    unit = models.CharField(max_length=20)
    storage = models.CharField(max_length=20, choices=STORAGE_TYPES)
    expiry_date = models.DateField()

    added_on = models.DateField(auto_now_add=True)
    @property
    def expiry_status(self):
        """Returns danger / warning / ok"""
        today = date.today()
        remaining = (self.expiry_date - today).days

        if remaining <= 1:
            return "danger"
        elif remaining <= 3:
            return "warning"
        return "ok"
    @property
    def expiry_text(self):
        """Readable expiry text"""
        today = date.today()
        remaining = (self.expiry_date - today).days

        if remaining < 0:
            return "Expired"
        elif remaining == 0:
            return "Today"
        else:
            return f"{remaining} days left"
    @property
    def freshness(self):
        """Simplified freshness indicator"""
        rem = (self.expiry_date - date.today()).days

        if rem >= 5:
            return "fresh"
        elif rem >= 2:
            return "medium"
        return "old"

    def __str__(self):
        return self.name
