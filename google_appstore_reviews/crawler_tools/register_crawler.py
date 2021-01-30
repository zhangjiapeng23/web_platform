#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @time  : 2021/1/30 6:09 下午


registered = list()


def register_crawler(func):
    registered.append(func())
    return func


def registered_project():
    return (pro for pro in registered)

