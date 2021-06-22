#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/6/22

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import UserInfo
from mobile_QA_web_platform.settings.base import LOCAL_HOST as host
from mobile_QA_web_platform.settings.base import LOCAL_PORT as port
from mobile_QA_web_platform.settings.base import MEDIA_URL


class UserInfoSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField()
    email = serializers.ReadOnlyField()
    is_superuser = serializers.ReadOnlyField()
    is_staff = serializers.ReadOnlyField()
    groups = serializers.StringRelatedField(many=True)
    permissions= serializers.StringRelatedField(many=True, source='user_permissions')


    class Meta:
        model = UserInfo
        fields = ('username', 'email', 'is_superuser', 'is_staff',
                  'first_name', 'last_name', 'groups', 'permissions', 'logo')


class MoreTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)
        data['access_token'] = str(refresh.access_token)
        data['username'] = self.user.username
        data['logo'] = host + ':' + port + MEDIA_URL + str(self.user.logo)
        data.pop('access')
        return data


