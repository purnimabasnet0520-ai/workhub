from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class UserNotification(models.Model):
    """Simple notification model for in-app notifications"""
    
    class NotificationType(models.TextChoices):
        INFO = "Info", "Info"
        SUCCESS = "Success", "Success"
        WARNING = "Warning", "Warning"
        ERROR = "Error", "Error"

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.CharField(max_length=500, blank=True, null=True)
    notification_type = models.CharField(choices=NotificationType.choices, default=NotificationType.INFO, max_length=20)
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["recipient", "-created_at"])]

    def __str__(self):
        return f"{self.recipient.username}: {self.message[:50]}"


class VerificationCode(models.Model):
    """Model for storing verification codes (OTP)"""

    class Purpose(models.TextChoices):
        REGISTER = "Register", "Register"
        LOGIN = "Login", "Login"
        CHANGE_PASSWORD = "Change Password", "Change Password"
        CHANGE_EMAIL = "Change Email", "Change Email"

    user = models.ForeignKey( User, on_delete=models.CASCADE, related_name="verification_codes" )
    code = models.CharField(max_length=6)
    purpose = models.CharField( choices=Purpose.choices, default=Purpose.REGISTER, max_length=20)
    is_used = models.BooleanField(default=False)
    is_expired = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    last_sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "purpose"]),
            models.Index(fields=["code", "purpose"]),
        ]

    def __str__(self):
        return f"{self.purpose} - {self.user.username} - {self.code}"

    def is_valid(self):
        """Check if the code is still valid"""
        from django.utils import timezone

        return (
            not self.is_used
            and not self.is_expired
            and self.expires_at > timezone.now()
        )
