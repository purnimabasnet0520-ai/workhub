from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .models import Job

@receiver(post_save, sender=Job)
def update_job_search_vector(sender, instance, **kwargs):
    instance.update_search_vector()

@receiver(m2m_changed, sender=Job.skills.through)
def update_job_skills_vector(sender, instance, **kwargs):
    instance.update_search_vector()
