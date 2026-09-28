from .models import Notification


def notifications(request):

    unread_notifications_count = 0

    if request.user.is_authenticated and request.user.role in ["teacher", "student"]:

        unread_notifications_count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()

    return {
        "unread_notifications_count": unread_notifications_count
    }