#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/6/24

import django_filters

from ..models import ReviewDetail


class ReviewFilter(django_filters.rest_framework.FilterSet):

    min_version = django_filters.NumberFilter(field_name='version', lookup_expr='gte')
    max_version = django_filters.NumberFilter(field_name='version', lookup_expr='lte')
    min_rating = django_filters.NumberFilter(field_name='rating', lookup_expr='gte')
    max_rating = django_filters.NumberFilter(field_name='rating', lookup_expr='lte')
    country = django_filters.CharFilter(field_name='review_info__country')

    class Meta:
        model = ReviewDetail
        fields = ['version', 'rating', 'country', 'min_version',
                  'max_version', 'min_rating', 'max_rating']
