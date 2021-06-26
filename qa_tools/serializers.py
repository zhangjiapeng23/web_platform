#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/6/25

from rest_framework import serializers

from . import models


class ProjectListSerializer(serializers.ModelSerializer):
    nid = serializers.ReadOnlyField()

    class Meta:
        model = models.Project
        fields = '__all__'

    def validate(self, attrs):
        name = attrs['name']
        try:
            models.Project.objects.get(name=name)
            raise serializers.ValidationError(f'{name} is existed')
        except models.Project.DoesNotExist:
            return attrs


class ProjectSerializer(serializers.ModelSerializer):
    nid = serializers.ReadOnlyField()
    name = serializers.CharField(max_length=40, required=False)
    scheme = serializers.CharField(max_length=40, required=False)
    api_key = serializers.CharField(max_length=128, required=False)
    instance_url = serializers.CharField(max_length=128, required=False)

    class Meta:
        model = models.Project
        fields = '__all__'

    def validate(self, attrs):
        name = attrs.get('name')
        if name is not None:
            try:
                models.Project.objects.get(name=name)
                raise serializers.ValidationError(f'{name} is existed')
            except models.Project.DoesNotExist:
                pass
        return attrs


class DisplayChoiceField(serializers.ChoiceField):

    def to_representation(self, value):
        return self._choices[value]


class NotificationListSerializer(serializers.ModelSerializer):
    nid = serializers.ReadOnlyField()
    project = serializers.StringRelatedField()
    push_type = DisplayChoiceField(choices=(
        (0, 'PUSH_TYPE'),
        (1, 'deeplink'),
        (2, 'general')
    ), help_text='0: PUSH_TYPE; 1: deeplink; 2: general')

    class Meta:
        model = models.Notification
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    nid = serializers.ReadOnlyField()
    project = serializers.StringRelatedField(read_only=True)
    push_type = DisplayChoiceField(choices=(
        (0, 'PUSH_TYPE'),
        (1, 'deeplink'),
        (2, 'general')
    ), help_text='0: PUSH_TYPE; 1: deeplink; 2: general', read_only=True)
    content = serializers.CharField(max_length=128, required=False)

    class Meta:
        model = models.Notification
        fields = '__all__'


class SdkConfigListSerializer(serializers.ModelSerializer):
    nid = serializers.ReadOnlyField()
    project = serializers.CharField(source='project_name', max_length=128)

    class Meta:
        model = models.SdkConifg
        fields = ('nid', 'project', 'app_key', 'config_type')


class SdkConfigSerializer(serializers.ModelSerializer):
    nid = serializers.ReadOnlyField()
    project = serializers.CharField(max_length=128, source='project_name', required=False)
    app_key = serializers.CharField(max_length=218, required=False)
    config_type = serializers.CharField(max_length=32, required=False)

    class Meta:
        model = models.SdkConifg
        fields = ('nid', 'project', 'app_key', 'config_type')

    def validate_app_key(self, value):
        try:
            models.SdkConifg.objects.get(app_key=value)
            raise serializers.ValidationError(f'{value} is existed')
        except models.SdkConifg.DoesNotExist:
            return value






