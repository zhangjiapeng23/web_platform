#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/6/23
from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'


class ReviewResultSetPagination(StandardResultsSetPagination):

    def get_paginated_response(self, data):
        """
        :param data: tuple: (base content, rating summary)
        :return:
        """
        review_list, rating_summary, countries, versions = data
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('rating_summary', rating_summary),
            ('countries', countries),
            ('versions', versions),
            ('results', review_list)
        ]))
