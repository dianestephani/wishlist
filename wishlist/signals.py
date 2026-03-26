import logging

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)

ADMIN_EMAIL = "diane.stephani@gmail.com"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def auto_add_admin_friend(sender, instance, created, **kwargs):
    """When a new user registers, automatically add Diane as a mutual friend
    and notify Diane about the new signup."""
    if not created:
        return

    from .models import Friendship, Notification, User

    try:
        admin_user = User.objects.get(email=ADMIN_EMAIL)
    except User.DoesNotExist:
        logger.warning("Admin user %s not found — skipping auto-friend.", ADMIN_EMAIL)
        return

    if instance.pk == admin_user.pk:
        return

    Friendship.objects.get_or_create(user=instance, friend=admin_user)
    Friendship.objects.get_or_create(user=admin_user, friend=instance)

    name = f"{instance.first_name} {instance.last_name}".strip() or instance.username
    Notification.objects.create(
        recipient=admin_user,
        sender=instance,
        type=Notification.NotifType.ACTIVITY,
        subject=f"New user signed up: {name}",
        content=f"{name} (@{instance.username}) just created an account and was added as your friend.",
    )
