from django.contrib import admin

from .models import AndroidBuild, AndroidProject, IosBuild, IosProject
# Register your models here.


@admin.register(AndroidBuild)
class AndroidBuildAdmin(admin.ModelAdmin):
    list_display = ['nid', 'package_name', 'package_version_name',
                    'snapshot']


@admin.register(AndroidProject)
class AndroidProjectAdmin(admin.ModelAdmin):
    list_display = ['nid', 'project_name', 'project_logo']


@admin.register(IosProject)
class IosProjectAdmin(admin.ModelAdmin):
    list_display = ['nid', 'project_name', 'project_logo']


@admin.register(IosBuild)
class IosBuildAdmin(admin.ModelAdmin):
    list_display = ['nid', 'project_id', 'project_version',
                    'x_framework']