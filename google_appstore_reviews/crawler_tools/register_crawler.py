#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @time  : 2021/1/30 6:09 下午

import asyncio
import datetime
import threading
from collections import abc, namedtuple, Counter
from typing import List
from threading import Thread

from google_appstore_reviews.crawler_tools.crawler import AppStoreCrawler, GoogleCrawler
from google_appstore_reviews.crawler_tools.frozen_json import FrozenJson
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
registered = list()


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


def registered_project():
    global registered
    registered = get_register_project()
    return (pro for pro in registered)


class CrawlerPerform:

    def __init__(self, appid_android: str, appid_ios: int, countries: List):
        self.appid_android = appid_android
        self.appid_ios = appid_ios
        self.countries = countries
        self.__resp_ios = dict()
        self.__resp_android = dict()

    @property
    def resp_ios(self):
        return self.__resp_ios

    @property
    def resp_android(self):
        return self.__resp_android

    def get_googleplay(self):
        pools = list()
        lang_count = Counter(country.lang for country in self.countries)
        lang_country = {}
        for item in self.countries:
            if item.lang not in lang_country.keys():
                lang_country[item.lang] = item.code

        for lang, count in lang_count.items():
            pools.append(CrawlerGoogleThread(crawler_obj=GoogleCrawler(country=lang, appid=self.appid_android,
                                                                       max_page=4 + count),
                                             country=lang_country.get(lang)))

        for t in pools:
            t.start()

        for t in pools:
            t.join()
            self.__resp_android.update(t.get_result())

    async def create_appstore(self):
        tasks = list()
        for country in self.countries:
            tasks.append(AppStoreCrawler(appid=self.appid_ios, country=country.code))
        to_do = [task.request_data() for task in tasks]
        to_do_iter = asyncio.as_completed(to_do)
        for future in to_do_iter:
            res = await future
            self.__resp_ios.update(res)

    def get_appstore(self):
        new_loop = asyncio.new_event_loop()
        t = threading.Thread(target=self.start_loop, args=(new_loop,))
        t.start()
        res = asyncio.run_coroutine_threadsafe(self.create_appstore(), new_loop)
        res.result()

    def start_loop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()


class CrawlerGoogleThread(Thread):

    def __init__(self, crawler_obj: GoogleCrawler, country):
        Thread.__init__(self)
        self.crawler_obj = crawler_obj
        self.country = country
        self.resp = dict()
        self.result = None

    def run(self):
        self.result = self.crawler_obj.request_data()

    def get_result(self):
        self.resp[self.country] = self.result
        return self.resp


class ProjectCrawler:

    def __init__(self, project_name, android_id: str, ios_id: str, countries: list):
        self.project_name = project_name
        self.countries = countries
        self.android_id = android_id
        self.ios_id = ios_id

    def run(self):
        spider = CrawlerPerform(appid_android=self.android_id, appid_ios=self.ios_id, countries=self.countries)

        if self.android_id:
            t_android = threading.Thread(target=spider.get_googleplay)
            t_android.start()

        if self.ios_id:
            t_ios = threading.Thread(target=spider.get_appstore)
            t_ios.start()

        if self.ios_id:
            t_ios.join(timeout=120)
        if self.android_id:
            t_android.join(timeout=120)

        ios_data = FrozenJson(spider.resp_ios)
        android_data = FrozenJson(spider.resp_android)

        ios_dict = dict()
        android_dict = dict()

        for country in self.countries:
            try:
                ios_dict[country.code] = getattr(ios_data, country.code)
            except AttributeError:
                code = country.code + '_'
                try:
                    ios_dict[country.code] = getattr(ios_data, code)
                except AttributeError:
                    continue

        android_countries = list({'us' if item.lang == 'en' and self.project_name == 'NBA'
                                  else item.code for item in self.countries})
        for country in android_countries:
            try:
                android_dict[country] = getattr(android_data, country)
            except AttributeError:
                country += '_'
                try:
                    android_dict[country] = getattr(android_data, country)
                except AttributeError:
                    continue

        pools = []
        for country, data in android_dict.items():
            if data is not None:
                pools.append(threading.Thread(target=self.write_data, args=(self.project_name, 'android', country, data)))

        for country, data in ios_dict.items():
            if data is not None:
                pools.append(threading.Thread(target=self.write_data, args=(self.project_name, 'ios', country, data)))

        for t in pools:
            t.start()

        for t in pools:
            t.join()
        print('crawler data write in db finish.')

    @staticmethod
    def write_data(project_name, platform, country, data):
        review_data = namedtuple('review', ['project_name', 'review_id', 'author', 'platform', 'country',
                                            'title', 'content', 'rating', 'version', 'time'])
        data_list = list()
        if platform == 'ios':
            platform = 1
            for page in range(len(data)):
                try:
                    content = data[page].feed.entry
                    date_time = ''.join(data[page].feed.updated.label.split('-')[0:3])
                    date_time = datetime.datetime.strptime(date_time, "%Y%m%dT%H:%M:%S")

                except AttributeError:
                    break
                # some data is not sequence object.
                if not isinstance(content, abc.MutableSequence):
                    content_temp = content
                    content = list()
                    content.append(content_temp)

                for item in range(len(content)):
                    wrap_data = review_data(project_name=project_name,
                                            review_id=content[item].id.label,
                                            author=content[item].author.name.label,
                                            platform=platform,
                                            country=country,
                                            title=content[item].title.label[0:128],
                                            content=content[item].content.label,
                                            rating=getattr(content[item], 'im:rating').label,
                                            version=getattr(content[item], 'im:version').label,
                                            time=date_time)
                    data_list.append(wrap_data)

        elif platform == 'android':
            platform = 0
            for item in range(len(data)):
                title = ' '.join(data[item].content.split(' ')[0:4]) if data[item].content else None
                wrap_data = review_data(project_name=project_name,
                                        review_id=data[item].reviewId,
                                        author=data[item].userName,
                                        platform=platform,
                                        country=country,
                                        title=title[0:128] if title else title,
                                        content=data[item].content,
                                        rating=data[item].score,
                                        version=data[item].reviewCreatedVersion,
                                        time=data[item].at)
                data_list.append(wrap_data)

        db = CrawlerDb()
        for data in data_list:
            nid = db.insert_data_to_reviewinfo(data[0:5])
            if nid is None:
                break
            else:
                db.insert_data_to_reviewdetail((nid, *data[5:]))

        db.commit()
        db.cursor_close()
        db.conn_close()

