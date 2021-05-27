#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @time  : 2021/1/30 6:02 下午

from collections import namedtuple

from google_appstore_reviews.crawler_tools.register_crawler import register_crawler, ProjectCrawler
from google_appstore_reviews.crawler_tools.db_operatoin import CrawlerDb

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
# New Zealand
nz = region('nz', 'en')

@register_crawler
def get_register_project():
    db = CrawlerDb()
    project_list = db.get_project_list()
    db.cursor_close()
    db.conn_close()
    register_projects = []

    def parse_region(region_code):
        position = 0
        register_region = []
        region_list = [us, au, ph, fr, china_tw, es, it, ca, ge, br, nz]
        while region_code > 0:
            if region_code & 1 == 1:
                register_region.append(region_list[position])
            region_code >>= 1
            position += 1
        return register_region

    for project in project_list:
        if project.get('is_active'):
            register_projects.append(ProjectCrawler(project_name=project.get('project_name'),
                                                    android_id=project.get('android_id'),
                                                    ios_id=project.get('ios_id'),
                                                    countries=parse_region(project.get('support_region'))))
    return register_projects






# @register_crawler
# def nba():
#     return ProjectCrawler(project_name='NBA',
#                           android_id='com.nbaimd.gametime.nba2011',
#                           ios_id='484672289',
#                           countries=[us, au, ph, fr, china_tw, es, it, ca, ge, br])
#
#
# @register_crawler
# def sky():
#     return ProjectCrawler(project_name='Fan_Pass',
#                           android_id='nz.co.skytv.fanpass',
#                           ios_id='941399309',
#                           countries=[nz])


if __name__ == '__main__':
    parse_region(337)