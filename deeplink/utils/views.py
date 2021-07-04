#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/7/3

from rest_framework import generics, status
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework.settings import api_settings


class BatchCreateModelMixin:
    """
    Create a model instance.
    """
    def create(self, request, *args, **kwargs):
        if isinstance(request.data, list):
            serializers_data = []
            for data in request.data:
                serializer = self.get_serializer(data=data)
                try:
                    serializer.is_valid(raise_exception=True)
                except Exception as e:
                    error_resp = {}
                    error = e.detail
                    print(error)
                    for key in error.keys():
                        value = error[key]
                        if isinstance(value, list):
                            error_resp[key] = value[0]
                        else:
                            error_resp[key] = value
                        error_resp[key] = error[key]
                    serializers_data.append(error_resp)
                    continue

                self.perform_create(serializer)
                response = serializer.data
                serializers_data.append(response)
        else:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            serializers_data = serializer.data
        headers = self.get_success_headers(serializer.data)
        return Response(serializers_data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}


class ListBatchCreateView(ListModelMixin,
                          BatchCreateModelMixin,
                          generics.GenericAPIView):

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
