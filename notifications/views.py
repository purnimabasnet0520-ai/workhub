from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import UserNotification


@login_required
@require_POST
def mark_all_notifications_read(request):
    UserNotification.objects.filter(
        recipient=request.user,
        is_read=False,
    ).update(is_read=True)

    return JsonResponse({"success": True})
