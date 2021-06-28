#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/6/26
import json
import re
from typing import List
from collections import deque

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

        def is_snapshot(library):
            return True if '-SNAPSHOT' in library['currentVersion'] else False

        def library_sorted(libraries: List, key=None):
            if key is None:
                return libraries
            sort_library = deque()
            for item in libraries:
                if key(item):
                    sort_library.appendleft(item)
                else:
                    sort_library.append(item)
            libraries[:] = sort_library

        library_list = json.loads(obj.library_coordinate_list)
        library_sorted(library_list, key=is_snapshot)
        return library_list


class BuildIosListSerializer(serializers.ModelSerializer):
    framework = serializers.SerializerMethodField()

    class Meta:
        model = models.IosBuild
        fields = '__all__'

    def get_framework(self, obj):

        def is_xframework(framework):
            if re.match(r'\d+\.\d+\.0\d+', framework['frameworkVersion']) \
                    or 'x' in framework['frameworkVersion']:
                return True
            return False

        def framework_sorted(frameworks: List, key=None):
            if key is None:
                return frameworks
            sort_frameworks = deque()
            for item in frameworks:
                if key(item):
                    sort_frameworks.appendleft(item)
                else:
                    sort_frameworks.append(item)
            frameworks[:] = sort_frameworks

        framework_list = json.loads(obj.framework)
        framework_sorted(framework_list, key=is_xframework)

        return framework_list

