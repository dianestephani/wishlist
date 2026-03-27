from .models import FriendRequest, Message, Notification


def unread_counts(request):
    if not request.user.is_authenticated:
        return {}

    unread_messages = (
        Message.objects.filter(conversation__participants=request.user, is_read=False)
        .exclude(sender=request.user)
        .count()
    )
    unread_notifications = Notification.objects.filter(
        recipient=request.user, is_read=False
    ).count()
    pending_friend_requests = FriendRequest.objects.filter(
        to_user=request.user, status=FriendRequest.Status.PENDING
    ).count()

    total_unread = unread_messages + unread_notifications + pending_friend_requests

    return {
        "unread_messages": unread_messages,
        "unread_notifications": unread_notifications,
        "pending_friend_requests": pending_friend_requests,
        "total_unread": total_unread,
    }
