#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/6/9
from .base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'web_platform',
        'USER': 'root',
        'PASSWORD': 'NeuMobile123$',
        'HOST': '127.0.0.1',
        'PORT': 3306

    }
}
