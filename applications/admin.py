from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import action
from .models import Application

class ApplicationAdmin(ModelAdmin):
    list_display = ('job', 'applicant', 'applied_at', 'status')
    search_fields = ('applicant__username', 'job__title')
    list_filter = ('status',)

admin.site.register(Application, ApplicationAdmin)
