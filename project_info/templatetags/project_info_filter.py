#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/3/8
import re

from django import template

register = template.Library()


@register.filter
def library_name_format(library_name: str):
    library_name = library_name.split(':')
    if len(library_name) > 1:
        return library_name[1]
    else:
        return library_name[0]


@register.filter
def ios_x_framework_check(framework_version: str):
    if re.match(r'\d+\.\d+\.0\d+', framework_version) \
            or 'x' in str(framework_version):
        return True
    else:
        return False


@register.filter
def is_library_need_upgrade(library_name, library_version):
    needupdate = ['5.0.0.x', '5.0.0', '5.0.02', '5.0.03', '5.0.04', '5.0.1', '5.0.1', '5.0.2', '5.0.3']
    if str(library_name) == 'NLTracking' and (int(str(library_version).replace('.', '')) < 448 or
                                             str(library_version) in needupdate):
        return True
    else:
        return False


