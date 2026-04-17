from django.contrib import admin
from unfold.admin import ModelAdmin, StackedInline
from unfold.decorators import action
from .models import *
from skills.models import Skill

class ExperienceInline(StackedInline):
    model = Experience
    extra = 1

class EducationInline(StackedInline):
    model = Education
    extra = 1

class CertificationInline(StackedInline):
    model = Certification
    extra = 1   

class SocialLinkInline(StackedInline):
    model = SocialLink
    extra = 1

class ProjectInline(StackedInline):
    model = Project
    extra = 1

class ProfileAdmin(ModelAdmin):
    list_display = ['id', 'user', 'role', 'position', 'address']
    list_filter = ['role', 'gender', 'preferred_work_mode', 'preferred_job_type']
    search_fields = ['user__username', 'user__email', 'position', 'address']
    inlines = [ExperienceInline, EducationInline, CertificationInline, SocialLinkInline, ProjectInline]  

from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

admin.site.unregister(User)

@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    pass

admin.site.register(Profile, ProfileAdmin)
