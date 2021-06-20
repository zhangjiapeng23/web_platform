#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/6/20

from rest_framework import serializers

from . import models


class ProjectSerializer(serializers.Serializer):
    nid = serializers.IntegerField(read_only=True)
    logo = serializers.FileField(read_only=True, required=False)
    name = serializers.CharField(max_length=64, required=True)

    def create(self, validated_data):
        return models.Project.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance






