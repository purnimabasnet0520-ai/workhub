from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import action
from .models import UserNotification, VerificationCode

@admin.register(UserNotification)
class UserNotificationAdmin(ModelAdmin):
    list_display = ['recipient', 'message', 'notification_type', 'is_read', 'created_at']
    list_filter = ['is_read', 'notification_type']
    search_fields = ['recipient__username', 'message']
    raw_id_fields = ['recipient']

@admin.register(VerificationCode)
class VerificationCodeAdmin(ModelAdmin):
    list_display = ['user', 'purpose', 'code', 'is_used', 'is_expired', 'created_at', 'expires_at']
    list_filter = ['purpose', 'is_used', 'is_expired']
    search_fields = ['user__username', 'user__email', 'code']
    raw_id_fields = ['user']
    readonly_fields = ['created_at', 'expires_at']
