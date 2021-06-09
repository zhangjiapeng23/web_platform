#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/6/9

from django import forms

from .models import UserInfo


class UserCreateForm(forms.Form):
    username = forms.CharField(required=True,
                               max_length=150)
    password = forms.CharField(required=True,
                               max_length=128,
                               min_length=6)
    confirm_password = forms.CharField(required=True,
                                       max_length=128,
                                       min_length=6)
    logo = forms.FileField(required=False)
    email = forms.EmailField(required=True)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        user = UserInfo.objects.filter(username=username).first()
        if user:
            self.add_error('username', f"{username} has been registered.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        email_record = UserInfo.objects.filter(email=email).first()
        if email_record:
            self.add_error('email', f'{email} has bee registered')
        return email

    def clean(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if confirm_password != password:
            self.add_error('confirm_password', "Two passwords don't match.")
        return self.cleaned_data


class UserLoginForm(forms.Form):
    username = forms.CharField(required=True,
                               max_length=150)
    password = forms.CharField(required=True,
                               max_length=128,
                               min_length=6)




