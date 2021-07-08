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


class TestcaseUpdateSerializer(serializers.ModelSerializer):
    project = serializers.ReadOnlyField(source='project.name')
    title = serializers.CharField(required=False, max_length=64)
    node_id = serializers.ReadOnlyField()
    description = serializers.CharField(required=False)

    class Meta:
        model = models.Testcase
        fields = '__all__'


class TestcaseProjectCreateSerializer(serializers.ModelSerializer):
    project = serializers.ReadOnlyField(source='project.name')

    class Meta:
        model = models.Testcase
        fields = '__all__'


class TestTaskListSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    project = ProjectSerializer()
    testcase = TestcaseSerializer(many=True)

    class Meta:
        model = models.TestTask
        fields = '__all__'


class TestTaskCreateSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = models.TestTask
        fields = '__all__'


class TestTaskProjectCreateSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    project = serializers.ReadOnlyField(source='project.name')

    class Meta:
        model = models.TestTask
        fields = '__all__'


class TaskReportSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Report
        fields = '__all__'


class TaskRecordSerializer(serializers.ModelSerializer):
    report = TaskReportSerializer(read_only=True)
    status = serializers.SerializerMethodField()

    class Meta:
        model = models.TaskExecuteRecord
        fields = '__all__'

    def get_status(self, obj):
        return obj.status






