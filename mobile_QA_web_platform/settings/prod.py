#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/6/9

from .base import *

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'web_platform',
        'USER': 'root',
        'PASSWORD': 'NeuMobile123$',
        'HOST': '139.159.179.26',
        'PORT': 30306
    }
}
