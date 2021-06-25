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


