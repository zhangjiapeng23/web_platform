#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/6/22

from rest_framework.views import exception_handler
from rest_framework.views import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    error_message = {}

    if response is None:
        print(context['view'], context['request'].method, exc)
        raise exc
        return Response({
            'error_message': {'detail': 'Server is error'}
        },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            exception=True
        )
    else:
        if isinstance(response.data, list):
            error_message = []
            for response_data in response.data:
                for key in response_data:
                    simple_error = {}
                    value = response_data[key]
                    if isinstance(value, str):
                        simple_error[key] = value
                    else:
                        simple_error[key] = value[0]

                    error_message.append(simple_error)

        else:
            for key in response.data:
                value = response.data[key]
                if isinstance(value, list):
                    error_message[key] = value[0]
                else:
                    error_message[key] = value

        return Response({
            'error_message': error_message
        },
            status=response.status_code,
            exception=True
        )






