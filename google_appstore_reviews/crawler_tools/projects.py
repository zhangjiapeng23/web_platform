#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @time  : 2021/1/30 6:02 下午

from collections import namedtuple

from google_appstore_reviews.crawler_tools.register_crawler import register_crawler, ProjectCrawler


region = namedtuple('country', ['code', 'lang'])

# United States
us = region('us', 'en')
# Australia
au = region('au', 'en')
# Philippine
ph = region('ph', 'en')
# France
fr = region('fr', 'fr')
# China Taiwan
china_tw = region('tw', 'zh')
# Spain
es = region('es', 'es')
# Italy
it = region('it', 'it')
# Canada
ca = region('cd', 'en')
# Germany
ge = region('de', 'de')
# Brazil
br = region('br', 'pt')
nz = region('nz', 'en')


@register_crawler
def nba():
    return ProjectCrawler(project_name='NBA',
                          android_id='com.nbaimd.gametime.nba2011',
                          ios_id='484672289',
                          countries=[us, au, ph, fr, china_tw, es, it, ca, ge, br])


@register_crawler
def sky():
    return ProjectCrawler(project_name='Fan_Pass',
                          android_id='nz.co.skytv.fanpass',
                          ios_id='941399309',
                          countries=[nz])
