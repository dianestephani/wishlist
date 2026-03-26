"""Helpers for creating messages and notifications."""
from .models import Conversation, Message, Notification


def get_or_create_conversation(user_a, user_b):
    """Get the single conversation between two users, or create one."""
    convos = Conversation.objects.filter(participants=user_a).filter(participants=user_b)
    if convos.exists():
        return convos.first()
    convo = Conversation.objects.create()
    convo.participants.add(user_a, user_b)
    return convo


def notify(sender, recipient, subject, content, notif_type, related_id=None):
    """Create a Notification only. No message thread."""
    return Notification.objects.create(
        recipient=recipient,
        sender=sender,
        type=notif_type,
        subject=subject,
        content=content,
        related_object_id=related_id,
    )


def send_message(sender, recipient, subject, content):
    """Create a Message in a conversation. Used for direct messages and replies."""
    convo = get_or_create_conversation(sender, recipient)
    return Message.objects.create(
        conversation=convo,
        sender=sender,
        subject=subject,
        content=content,
    )
