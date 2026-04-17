from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import action
from .models import Company

class CompanyAdmin(ModelAdmin):
    list_display = ('id', 'name', 'public_url', 'created_by', 'created_at')
    search_fields = ('name', 'public_url', 'created_by__username')
    prepopulated_fields = {'public_url': ('name',)}


admin.site.register(Company, CompanyAdmin)