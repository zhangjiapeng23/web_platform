#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/6/24

from rest_framework import serializers

from . import models



class ProjectListSerializer(serializers.ModelSerializer):
    nid = serializers.ReadOnlyField()
    name = serializers.CharField(max_length=32, required=True)
    scheme = serializers.CharField(max_length=64, required=True)

    class Meta:
        model = models.Project
        fields = '__all__'


    def validate_name(self, value):
        try:
            models.Project.objects.get(name=value)
            raise serializers.ValidationError(f'{value} is existed')
        except models.Project.DoesNotExist:
            return value


class ProjectSerializer(serializers.ModelSerializer):
    nid = serializers.ReadOnlyField()
    name = serializers.CharField(max_length=32, required=False)
    scheme = serializers.CharField(max_length=64, required=False)

    class Meta:
        model = models.Project
        fields = '__all__'

    def validate_name(self, value):
        try:
            models.Project.objects.get(name=value)
            raise serializers.ValidationError(f'{value} is existed')
        except models.Project.DoesNotExist:
            return value


class DeeplinkContentListSerializer(serializers.ModelSerializer):
    nid = serializers.ReadOnlyField()
    body = serializers.CharField(max_length=128)
    create_time = serializers.ReadOnlyField()
    classification = serializers.ReadOnlyField()
    project = serializers.StringRelatedField(source='Project')
    deeplink = serializers.SerializerMethodField()

    class Meta:
        model = models.Contents
        fields = ('nid', 'body', 'create_time', 'classification', 'project', 'deeplink')

    def get_deeplink(self, obj):
        body_format = '%s://%s'
        body = obj.body
        scheme = models.Project.objects.get(pk=obj.project_id).scheme
        if body.startswith('http'):
            return body
        else:
            return body_format % (scheme, body)


class DeeplinkContentCreateSerializer(serializers.ModelSerializer):
    nid = serializers.ReadOnlyField()
    body = serializers.CharField(max_length=128)
    create_time = serializers.ReadOnlyField()
    classification = serializers.CharField(max_length=32, required=False)
    project = serializers.ReadOnlyField(source='project.name')
    deeplink = serializers.SerializerMethodField()

    class Meta:
        model = models.Contents
        fields = ('nid', 'body', 'create_time', 'classification', 'project', 'deeplink')

    def get_deeplink(self, obj):
        project = self.context['view'].kwargs.get('project')
        body = obj.body
        return self._get_deeplink(project, body)

    def _get_deeplink(self, project, body):
        body_format = '%s://%s'
        scheme = models.Project.objects.get(name=project).scheme
        if body.startswith('http'):
            return body
        else:
            return body_format % (scheme, body)


class DeeplinkSerializer(serializers.ModelSerializer):
    nid = serializers.ReadOnlyField()
    body = serializers.CharField(max_length=128, required=False)
    classification = serializers.CharField(max_length=32, required=False)
    project = serializers.StringRelatedField(source='project.name')
    deeplink = serializers.SerializerMethodField()
    create_time = serializers.ReadOnlyField()

    class Meta:
        model = models.Contents
        fields = '__all__'

    def get_deeplink(self, obj):
        project = self.context['view'].kwargs.get('project')
        body = obj.body
        return self._get_deeplink(project, body)

    def _get_deeplink(self, project, body):
        body_format = '%s://%s'
        scheme = models.Project.objects.get(name=project).scheme
        if body.startswith('http'):
            return body
        else:
            return body_format % (scheme, body)













