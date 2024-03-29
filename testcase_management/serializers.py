#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/6/20

from rest_framework import serializers

from . import models


class ProjectSerializer(serializers.Serializer):
    nid = serializers.IntegerField(read_only=True)
    logo = serializers.FileField(required=False)
    name = serializers.CharField(max_length=64, required=True)

    def create(self, validated_data):
        return models.Project.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.logo = validated_data.get('logo', instance.logo)
        instance.save()
        return instance

    def validate_name(self, value):
        try:
            models.Project.objects.get(name=value)
            raise serializers.ValidationError(f'{value} is already existed')
        except models.Project.DoesNotExist:
            return value


class TestcaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Testcase
        fields = '__all__'


class TestTaskSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = models.TestTask
        fields = '__all__'


class ReportSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Report
        fields = '__all__'



