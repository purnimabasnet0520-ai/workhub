from django.urls import path

from .views import mark_all_notifications_read

urlpatterns = [
    path("mark-all-read/", mark_all_notifications_read, name="mark_all_notifications_read"),
]
