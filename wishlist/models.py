import random

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

AVATAR_COLORS = [
    "#5eead4", "#f472b6", "#818cf8", "#fb923c", "#a78bfa",
    "#34d399", "#f87171", "#60a5fa", "#fbbf24", "#c084fc",
]


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True)
    avatar_color = models.CharField(max_length=7, blank=True)

    def save(self, *args, **kwargs):
        if not self.avatar_color:
            self.avatar_color = random.choice(AVATAR_COLORS)
        super().save(*args, **kwargs)

    @property
    def initials(self):
        first = self.first_name[0] if self.first_name else "?"
        last = self.last_name[0] if self.last_name else ""
        return f"{first}{last}"

    def __str__(self):
        return self.email


class Wishlist(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlists",
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class Event(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="events_created",
    )
    title = models.CharField(max_length=255)
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    address = models.CharField(max_length=500, blank=True)
    notes = models.TextField(blank=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return self.title


class Activity(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="activities_created",
    )
    title = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "activities"

    def __str__(self):
        return self.title


class WishlistItem(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "available", "Available"
        PURCHASED = "purchased", "Purchased"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlist_items",
    )
    wishlist = models.ForeignKey(
        Wishlist,
        on_delete=models.CASCADE,
        related_name="items",
        null=True,
        blank=True,
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


class Friendship(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="friendships",
    )
    friend = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="friended_by",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "friend")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} ↔ {self.friend}"


class FriendRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        DENIED = "denied", "Denied"

    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_requests",
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_requests",
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("from_user", "to_user")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.from_user} → {self.to_user} ({self.status})"


class Conversation(models.Model):
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="conversations",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def other_participant(self, user):
        return self.participants.exclude(pk=user.pk).first()

    def last_message(self):
        return self.messages.order_by("-created_at").first()

    def __str__(self):
        names = ", ".join(str(p) for p in self.participants.all()[:2])
        return f"Conversation: {names}"


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_messages",
    )
    subject = models.CharField(max_length=255)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.sender}: {self.subject}"


class Notification(models.Model):
    class NotifType(models.TextChoices):
        WISHLIST = "wishlist", "Wishlist"
        EVENT = "event", "Event"
        ACTIVITY = "activity", "Activity"

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_notifications",
        null=True,
        blank=True,
    )
    type = models.CharField(max_length=10, choices=NotifType.choices)
    subject = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    related_object_id = models.IntegerField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.type}] {self.subject}"
