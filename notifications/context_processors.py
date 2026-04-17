from .models import UserNotification


def notification_data(request):
    if not request.user.is_authenticated:
        return {
            "navbar_notifications": [],
            "unread_notifications_count": 0,
        }

    notifications = list(
        UserNotification.objects.filter(recipient=request.user).order_by("-created_at")[:10]
    )
    unread_count = UserNotification.objects.filter(
        recipient=request.user,
        is_read=False,
    ).count()

    return {
        "navbar_notifications": notifications,
        "unread_notifications_count": unread_count,
    }
