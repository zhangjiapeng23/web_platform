#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/6/14
from datetime import timedelta

from django.utils import timezone
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication
from django.utils.translation import ugettext_lazy as _

from mobile_QA_web_platform.settings.base import TOKEN_EXPIRE


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

        return token.user, token



