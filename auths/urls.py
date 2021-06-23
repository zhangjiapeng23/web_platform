#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/6/22

from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^login/$', views.Login.as_view(), name='login'),
    re_path(r'^refreshToken/$', views.TokenRefreshView.as_view(), name='refresh_token'),
    re_path(r'^register/$', views.Register.as_view(), name='register'),
    re_path(r'^profile/$', views.Profile.as_view(), name='account_info'),
    re_path(r'^password/$', views.ModifyPassword.as_view(), name='modify_password')
]