from django.contrib import admin

from .models import Project, Notification
# Register your models here.

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['nid', 'name', 'api_key']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['nid', 'project', 'get_type_display']



