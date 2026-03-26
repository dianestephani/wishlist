from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.email


class WishlistItem(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "available", "Available"
        PURCHASED = "purchased", "Purchased"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlist_items",
    )
    title = models.CharField(max_length=255)
    product_url = models.URLField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    category = models.CharField(max_length=100, blank=True)
    brand = models.CharField(max_length=100, blank=True)
    store = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to="wishlist_images/", blank=True)
    notes = models.TextField(blank=True)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.AVAILABLE,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Purchase(models.Model):
    item = models.OneToOneField(
        WishlistItem,
        on_delete=models.CASCADE,
        related_name="purchase",
    )
    purchased_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="purchases",
    )
    message = models.TextField(blank=True)
    purchased_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item.title} purchased by {self.purchased_by}"


class ItemEvent(models.Model):
    class EventType(models.TextChoices):
        PURCHASED = "purchased", "Marked as Purchased"
        UNDONE = "undone", "Purchase Undone"

    item = models.ForeignKey(
        WishlistItem,
        on_delete=models.CASCADE,
        related_name="events",
    )
    event_type = models.CharField(max_length=10, choices=EventType.choices)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="item_events",
    )
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.item.title} — {self.get_event_type_display()} by {self.user}"


class ItemView(models.Model):
    item = models.ForeignKey(
        WishlistItem,
        on_delete=models.CASCADE,
        related_name="views",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="item_views",
    )
    count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("item", "user")

    def __str__(self):
        return f"{self.user} viewed {self.item.title} ({self.count}x)"


class StoreClick(models.Model):
    item = models.ForeignKey(
        WishlistItem,
        on_delete=models.CASCADE,
        related_name="store_clicks",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="store_clicks",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} clicked store for {self.item.title}"
