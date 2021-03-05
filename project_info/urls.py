#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/3/5
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name='index'),
    path("AndroidProjectList/", views.android_project_list, name='android_project_list'),
    path("iOSProjectList/", views.ios_project_list, name='ios_project_list'),
    path("AndroidProjectList/<str:project>", views.android_project_detail, name='android_project_detail'),
    path("iOSProjectList/<str:project>", views.ios_project_detail, name='ios_project_detail'),
    path("AndroidLibraryDetail/", views.android_library_detail, name='android_library_detail'),
    path("iOSLibraryDetail/", views.ios_library_detail, name='ios_library_detail'),
    path("NLAndroid/", views.android_upload_api, name='android_upload_api'),
    path("NLiOS/", views.ios_upload_api, name='ios_upload_api'),
]