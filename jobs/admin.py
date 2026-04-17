from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import action
from django.urls import reverse_lazy
from .models import Job

class JobAdmin(ModelAdmin):
    list_display = ("title", "company", "recruiter", "location", "employment_type", "work_mode", "created_at", "is_active")
    search_fields = ("title", "company__name", "location", "recruiter__username")
    list_filter = ("employment_type", "work_mode", "created_at", "is_active")
    ordering = ("-created_at",)
    
admin.site.register(Job, JobAdmin)

