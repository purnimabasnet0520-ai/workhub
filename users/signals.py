# accounts/signals.py
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile, Experience, Education, Certification, Project


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=Profile)
def update_profile_search_vector(sender, instance, **kwargs):
    instance.update_search_vector()

@receiver(m2m_changed, sender=Profile.skills.through)
def update_profile_skills_vector(sender, instance, **kwargs):
    instance.update_search_vector()

def update_related_profile_vector(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.update_search_vector()

post_save.connect(update_related_profile_vector, sender=Experience)
post_delete.connect(update_related_profile_vector, sender=Experience)
post_save.connect(update_related_profile_vector, sender=Education)
post_delete.connect(update_related_profile_vector, sender=Education)
post_save.connect(update_related_profile_vector, sender=Certification)
post_delete.connect(update_related_profile_vector, sender=Certification)
post_save.connect(update_related_profile_vector, sender=Project)
post_delete.connect(update_related_profile_vector, sender=Project)
