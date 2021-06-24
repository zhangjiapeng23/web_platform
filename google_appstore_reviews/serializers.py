#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/6/23

from rest_framework import serializers

from . import models


class ProjectListSerializer(serializers.ModelSerializer):
    nid = serializers.ReadOnlyField()
    project_name = serializers.CharField(max_length=64, required=True)
    is_active = serializers.BooleanField(default=True, required=False)
    android_id = serializers.CharField(max_length=128, required=False)
    ios_id = serializers.CharField(max_length=128, required=False)
    support_region = serializers.IntegerField(required=True)
    project_logo = serializers.FileField(required=False)
    android_origin = serializers.CharField(max_length=256, required=False)
    ios_origin = serializers.CharField(max_length=256, required=False)

    class Meta:
        model = models.Project
        fields = ('nid', 'project_name', 'is_active', 'android_id', 'ios_id',
                  'support_region', 'project_logo', 'android_origin', 'ios_origin')

    def validate_project_name(self, value):
        project_name = value.replace(' ', '_')
        try:
            models.Project.objects.get(project_name=project_name)
            raise serializers.ValidationError(f'{value} has existed')
        except models.Project.DoesNotExist:
            return project_name

    def validate(self, data):
        if not data.setdefault('android_origin', None) and data.setdefault('android_id', None):
            data['android_origin'] = f'https://play.google.com/store/apps/details?id={data["android_id"]}' \
                                     f'&showAllReviews=true'
        if not data.setdefault('ios_origin', None) and data.setdefault('ios_id', None):
            data['ios_origin'] = f'https://itunes.apple.com/rss/customerreviews/page=1/id={data["ios_id"]}/' \
                                 f'sortby=mostrecent/json'

        return data


class ProjectSerializer(serializers.ModelSerializer):
    nid = serializers.ReadOnlyField()
    project_name = serializers.ReadOnlyField()
    is_active = serializers.BooleanField(default=True, required=False)
    android_id = serializers.CharField(max_length=128, required=False)
    ios_id = serializers.CharField(max_length=128, required=False)
    support_region = serializers.IntegerField(required=False)
    project_logo = serializers.FileField(required=False)
    android_origin = serializers.CharField(max_length=256, required=False)
    ios_origin = serializers.CharField(max_length=256, required=False)

    class Meta:
        model = models.Project
        fields = '__all__'


class ReviewInfoListSerializer(serializers.ModelSerializer):
    nid = serializers.ReadOnlyField()
    review_id = serializers.ReadOnlyField()
    author = serializers.ReadOnlyField()
    platform = serializers.ReadOnlyField(source='get_platform_display')
    country = serializers.ReadOnlyField()
    project_name = serializers.StringRelatedField(source='project_name_id')

    class Meta:
        model = models.ReviewInfo
        fields = ('nid', 'review_id', 'author', 'platform', 'country', 'project_name')


class ReviewDetailListSerializer(serializers.ModelSerializer):
    review_info = ReviewInfoListSerializer(read_only=True)

    class Meta:
        model = models.ReviewDetail
        fields = '__all__'



