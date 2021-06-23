#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/6/8
from functools import reduce

from django import forms

from .models import Project


class ProjectForm(forms.Form):
    project_name = forms.CharField(required=True,
                                   max_length=128,
                                   error_messages={'required': 'Project name is required.'})
    support_region = forms.CharField(required=True,
                                     error_messages={'required': 'Project region is required.'})
    android_id = forms.CharField(required=False)
    ios_id = forms.CharField(required=False)
    project_logo = forms.FileField(required=False)


    def clean_project_name(self):
        origin_project_name = self.cleaned_data.get('project_name')
        project_name = origin_project_name.replace(' ', '_')
        res = Project.objects.filter(project_name=project_name).first()
        if res:
            self.add_error('project_name', f'{origin_project_name} project name has been used')
        return project_name

    def clean_support_region(self):
        support_region = self.cleaned_data.get('support_region')
        support_region = reduce(lambda x, y: int(x) + int(y), support_region.split(','))
        return support_region





