#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/6/22

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from django.contrib.auth.hashers import make_password, check_password

from .models import UserInfo
from mobile_QA_web_platform.settings.base import MEDIA_URL, HTTP_PROTOCOL


class UserInfoSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField()
    email = serializers.ReadOnlyField()
    is_superuser = serializers.ReadOnlyField()
    is_staff = serializers.ReadOnlyField()
    groups = serializers.StringRelatedField(many=True, required=False)
    permissions = serializers.StringRelatedField(many=True, source='user_permissions', required=False)

    class Meta:
        model = UserInfo
        fields = ('username', 'email', 'is_superuser', 'is_staff',
                  'first_name', 'last_name', 'groups', 'permissions', 'logo')


class CreateUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150, required=True)
    email = serializers.EmailField(max_length=254, required=True)
    password = serializers.CharField(max_length=128, required=True, write_only=True)
    confirm_password = serializers.CharField(max_length=128, required=True, write_only=True)
    logo = serializers.FileField(required=False)

    class Meta:
        model = UserInfo
        fields = ('username', 'email', 'password', 'confirm_password', 'logo')

    def validate(self, data):
        if data['password'] != data.pop('confirm_password'):
            raise serializers.ValidationError("Password do not match")
        data['password'] = make_password(data['password'])
        return data

    def validate_username(self, value):
        try:
            UserInfo.objects.get(username=value)
            raise serializers.ValidationError(f"Username {value} has been registered")
        except UserInfo.DoesNotExist:
            return value

    def validate_email(self, value):
        try:
            UserInfo.objects.get(email=value)
            raise serializers.ValidationError(f"E-mail {value} has been registered")
        except UserInfo.DoesNotExist:
            return value


class ModifyPasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, required=True)
    confirm_password = serializers.CharField(max_length=128, write_only=True, required=True)
    old_password = serializers.CharField(max_length=128, write_only=True, required=True)

    class Meta:
        model = UserInfo
        fields = ('password', 'confirm_password', 'old_password')

    def validate_old_password(self, value):
        if not check_password(value, self.user.password):
            raise serializers.ValidationError('Old password is incorrect')
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('confirm_password'):
            raise serializers.ValidationError('Password do not match')
        return attrs


class MoreTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        data['access_token'] = data['access']
        data['username'] = self.user.username
        data['logo'] = HTTP_PROTOCOL + self.context['request'].get_host() \
                       + MEDIA_URL + str(self.user.logo)
        data.pop('access')
        return data


class MoreTokenRefreshSerializer(TokenRefreshSerializer):

    def validate(self, attrs):
        data = super(MoreTokenRefreshSerializer, self).validate(attrs)
        data['access_token'] = data['access']
        data.pop('access')
        return data




