#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/7/3

from rest_framework import generics
from rest_framework.mixins import ListModelMixin

from mobile_QA_web_platform.utils.views_mixin import BatchCreateModelMixin


class ListBatchCreateView(ListModelMixin,
                          BatchCreateModelMixin,
                          generics.GenericAPIView):

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
