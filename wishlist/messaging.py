"""Helpers for creating messages and notifications together."""
from .models import Conversation, Message, Notification


def get_or_create_conversation(user_a, user_b):
    """Get the single conversation between two users, or create one."""
    convos = Conversation.objects.filter(participants=user_a).filter(participants=user_b)
    if convos.exists():
        return convos.first()
    convo = Conversation.objects.create()
    convo.participants.add(user_a, user_b)
    return convo


def send_message_and_notify(sender, recipient, subject, content, notif_type, related_id=None):
    """Create both a Message in a conversation and a Notification."""
    convo = get_or_create_conversation(sender, recipient)
    msg = Message.objects.create(
        conversation=convo,
        sender=sender,
        subject=subject,
        content=content,
    )
    Notification.objects.create(
        recipient=recipient,
        sender=sender,
        type=notif_type,
        subject=subject,
        content=content,
        related_object_id=related_id,
    )
    return msg
