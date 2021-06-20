#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/6/20
from django.urls import path, re_path
from . import views


urlpatterns = [
    re_path(r'projects/$', views.ProjectList.as_view(), name='project_list'),
    re_path('projects/(?P<pk>[0-9]+)/$', views.Project.as_view(), name='project'),
]
