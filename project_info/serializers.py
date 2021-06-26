#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/6/26
import json

from rest_framework import serializers

from . import models


class ProjectAndroidListSerializer(serializers.ModelSerializer):
    nid = serializers.ReadOnlyField()
    project = serializers.CharField(source='project_name', max_length=128)
    update_date = serializers.DateTimeField(required=False)

    class Meta:
        model = models.AndroidProject
        fields = ('nid', 'project', 'project_logo', 'update_date')

    def validate_project(self, value):
        try:
            models.AndroidProject.objects.get(project_name=value)
            raise serializers.ValidationError(f'{value} is existed')
        except models.AndroidProject.DoesNotExist:
            return value


class ProjectAndroidSerializer(serializers.ModelSerializer):
    nid = serializers.ReadOnlyField()
    project = serializers.CharField(source='project_name', max_length=128, required=False)
    update_date = serializers.DateTimeField(required=False)

    class Meta:
        model = models.AndroidProject
        fields = ('nid', 'project', 'project_logo', 'update_date')

    def validate_project(self, value):
        try:
            models.AndroidProject.objects.get(project_name=value)
            raise serializers.ValidationError(f'{value} is existed')
        except models.AndroidProject.DoesNotExist:
            return value


class ProjectIOSListSerializer(serializers.ModelSerializer):
    nid = serializers.ReadOnlyField()
    project = serializers.CharField(source='project_name', max_length=128)
    update_date = serializers.DateTimeField(required=False)

    class Meta:
        model = models.IosProject
        fields = ('nid', 'project', 'project_logo', 'update_date')

    def validate_project(self, value):
        try:
            models.IosProject.objects.get(project_name=value)
            raise serializers.ValidationError(f'{value} is existed')
        except models.IosProject.DoesNotExist:
            return value


class ProjectIOSSerializer(serializers.ModelSerializer):
    nid = serializers.ReadOnlyField()
    project = serializers.CharField(source='project_name', max_length=128, required=False)
    update_date = serializers.DateTimeField(required=False)

    class Meta:
        model = models.IosProject
        fields = ('nid', 'project', 'project_logo', 'update_date')

    def validate_project(self, value):
        try:
            models.IosProject.objects.get(project_name=value)
            raise serializers.ValidationError(f'{value} is existed')
        except models.IosProject.DoesNotExist:
            return value


class BuildAndroidListSerializer(serializers.ModelSerializer):
    library_coordinate_list = serializers.SerializerMethodField()

    class Meta:
        model = models.AndroidBuild
        fields = '__all__'

    def get_library_coordinate_list(self, obj):
        return json.loads(obj.library_coordinate_list)


class BuildIosListSerializer(serializers.ModelSerializer):
    framework = serializers.SerializerMethodField()

    class Meta:
        model = models.IosBuild
        fields = '__all__'

    def get_framework(self, obj):
        return json.loads(obj.framework)

