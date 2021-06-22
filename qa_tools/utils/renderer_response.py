#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/6/22

from rest_framework.renderers import JSONRenderer


class CustomRenderer(JSONRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if renderer_context:
            if isinstance(data, dict):
                status = data.pop('status', 'success')
                code = data.pop('code', '1')
            else:
                status = 'success'
                code = 1

            for key in data:
                if key == 'error_message':
                    status = 'fail'
                    data = data[key]
                    code = 0

            resp = {
                'status': status,
                'code': code,
                'data': data
                }
            return super().render(resp, accepted_media_type, renderer_context)
        else:
            return super().render(data, accepted_media_type, renderer_context)

