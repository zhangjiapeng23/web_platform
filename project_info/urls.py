#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/3/5
from django.urls import path, re_path

from . import views

urlpatterns = [
    re_path(r'^Android_projects/$', views.ProjectAndroidList.as_view(), name='project_Android_list'),
    re_path(r'^Android_projects/(?P<pk>[0-9]+)/$', views.ProjectAndroid.as_view(), name='project_Android'),
    re_path(r'^iOS_projects/$', views.ProjectIosList.as_view(), name='project_iOS_list'),
    re_path(r'^iOS_projects/(?P<pk>[0-9]+)/$', views.ProjectIos.as_view(), name='project_iOS'),
    re_path(r'^Android_builds/(?P<project>[0-9a-zA-Z\_]+)/$',
            views.BuildAndroidList.as_view(), name='build_Android_list'),
    re_path(r'^Android_builds/(?P<project>[0-9a-zA-Z\_]+)/(?P<pk>[0-9]+)/$',
            views.BuildAndroid.as_view(), name='build_Android'),
    re_path(r'^iOS_builds/(?P<project>[0-9a-zA-Z]+)/$',
            views.BuildIosList.as_view(), name='build_ios_list'),
    re_path(r'^iOS_builds/(?P<project>[0-9a-zA-Z]+)/(?P<pk>[0-9]+)/$',
            views.BuildIos.as_view(), name='build_ios'),
    path("", views.index, name='index'),
    path("AndroidProjectList/", views.android_project_list, name='android_project_list'),
    path("iOSProjectList/", views.ios_project_list, name='ios_project_list'),
    path("AndroidProjectList/<str:project>/", views.android_project_detail, name='android_project_detail'),
    path("iOSProjectList/<str:project>/", views.ios_project_detail, name='ios_project_detail'),
    path("AndroidLibraryDetail/", views.android_library_detail, name='android_library_detail'),
    path("iOSLibraryDetail/", views.ios_library_detail, name='ios_library_detail'),

]