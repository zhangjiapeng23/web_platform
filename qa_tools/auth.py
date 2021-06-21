#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/6/14
from datetime import timedelta

from django.utils import timezone
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

from mobile_QA_web_platform.settings.base import TOKEN_EXPIRE

UserModel = get_user_model()


class TokenExpireAuthentication(TokenAuthentication):

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

        if timezone.now() > (token.created + timedelta(seconds=TOKEN_EXPIRE)):
            raise exceptions.AuthenticationFailed(_('Token has expired'))

        return (token.user, token)


class UsernameOrEmailBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username is None or password is None:
            return
        try:
            # user = UserModel._default_manager.get_by_natural_key(username)
            user = UserModel.objects.get(Q(username=username) | Q(email=username))
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user


