from django.contrib import admin

from .models import Project, Notification, SdkConifg
# Register your models here.


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['nid', 'name', 'api_key']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['nid', 'project', 'get_push_type_display', 'content']


@admin.register(SdkConifg)
class SdkConfigAdmin(admin.ModelAdmin):
    list_display = ['nid', 'project_name', 'config_type', 'app_key']



