#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/6/23

from rest_framework import serializers
from django.db.models import Avg, Count

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


class ReviewRatingSummarySerializer(serializers.ModelSerializer):
    rating_summary = serializers.SerializerMethodField()

    class Meta:
        model = models.ReviewDetail
        fields = ('rating_summary',)

    def get_rating_summary(self, obj):
        response = {}
        rating_avg = obj.aggregate(avg=Avg('rating'))
        rating_count = obj.aggregate(count=Count('rating'))
        rating_percent = [obj.filter(rating=i).count() / rating_count['count']
                          if rating_count['count'] > 0 else 0 for i in range(1, 6)]
        rating_percent_format = ['{0:.2%}'.format(i) for i in rating_percent]
        response.update(rating_avg)
        response.update(rating_count)
        response['rating_percent'] = rating_percent_format
        return response


class ReviewCountrySerializer(serializers.ModelSerializer):
    countries = serializers.SerializerMethodField()

    class Meta:
        model = models.ReviewInfo
        fields = ('countries',)

    def get_countries(self, obj):
        country = obj.values_list('country').distinct().order_by('country')
        country = [i[0] for i in country]
        return country


class ReviewVersionSerializer(serializers.ModelSerializer):
    versions = serializers.SerializerMethodField()

    class Meta:
        model = models.ReviewDetail
        fields = ('versions', )

    def get_versions(self, obj):
        versions = obj.values_list('version').distinct().order_by('create_time')
        versions = [i[0] for i in versions]
        return versions


