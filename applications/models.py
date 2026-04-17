from django.db import models
from django.contrib.auth.models import User
from jobs.models import Job
from users.models import Profile


class Application(models.Model):

    class STATUS_CHOICES (models.TextChoices):
        Applied =   "applied", "Applied"
        Reviewing = "reviewing", "Reviewing"
        Shortlisted =  "shortlisted", "Shortlisted"
        Rejected =  "rejected", "Rejected"
        Hired =  "hired", "Hired"

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name="applications")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="applied")
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("job", "applicant")
        ordering = ["-applied_at"]

    def __str__(self):
        return f"{self.applicant.username} → {self.job.title}"
