#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/6/20
from django.urls import path, re_path
from . import views


urlpatterns = [
    re_path(r'projects/$', views.ProjectList.as_view(), name='project_list'),
    re_path(r'projects/(?P<pk>[0-9]+)/$', views.Project.as_view(), name='project'),
    re_path(r'^testcases/$', views.TestcaseList.as_view(), name='testcase_list'),
    re_path(r'^testcases/(?P<pk>[0-9]+)/$', views.Testcase.as_view(), name='testcase'),
    re_path(r'^test_tasks/$', views.TestTaskList.as_view(), name='test_task_list'),
    re_path(r'^test_tasks/(?P<pk>[0-9]+)/$', views.TestTask.as_view(), name='test_task'),
    re_path(r'^test_reports/$', views.TestTaskList.as_view(), name='test_report_list'),
    re_path(r'^test_reprots/(?P<pk>[0-9]+)/$', views.TestReport.as_view(), name='test_report'),

]
