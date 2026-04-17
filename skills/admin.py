from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import action
from .models import Skill

class SkillAdmin(ModelAdmin):
    list_display = ['id', 'name', 'is_active']

admin.site.register(Skill, SkillAdmin)
