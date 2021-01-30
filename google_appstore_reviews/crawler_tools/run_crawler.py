import datetime
import time
import threading
from typing import List
from threading import Thread
import asyncio
from collections import namedtuple, Counter
from collections import abc

from google_appstore_reviews.crawler_tools.db_operatoin import CrawlerDb
from google_appstore_reviews.crawler_tools.crawler import GoogleCrawler, AppStoreCrawler
from google_appstore_reviews.crawler_tools.frozen_json import FrozenJson
from google_appstore_reviews.crawler_tools.register_crawler import registered_project
from google_appstore_reviews.crawler_tools.projects import *

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


class ProjectCrawler:

    def __init__(self, project_name, android_id: str, ios_id: str, countries: list):
        self.project_name = project_name
        self.countries = countries
        self.android_id = android_id
        self.ios_id = ios_id

    def run(self):
        spider = CrawlerPerform(appid_android=self.android_id, appid_ios=self.ios_id, countries=self.countries)
        t_ios = threading.Thread(target=spider.get_appstore)
        t_android = threading.Thread(target=spider.get_googleplay)
        t_ios.start()
        t_android.start()
        t_ios.join(timeout=60)
        t_android.join(timeout=60)

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
        db.conn_colse()


def main(h, m):
    for pro in registered_project():
        pro.run()

    while True:
        while True:
            now = datetime.datetime.now()

            if now.hour == h and now.minute == m:
                break
            else:
                time.sleep(60)

        for pro in registered_project():
            pro.run()
        time.sleep(60)


def crawler_start(hour=23, minute=0):
    t = threading.Thread(target=main, args=(hour, minute))
    t.start()


if __name__ == '__main__':
    crawler_start(0, 0)
    # region = namedtuple('country', ['code', 'lang'])
    # nz = region('nz', 'en')
    # countries = [nz]
    # sky = ProjectCrawler(project_name='Fan Pass',
    #                      android_id='nz.co.skytv.fanpass',
    #                      ios_id='941399309',
    #                      countries=[nz])
    # sky.run()
    # test = CrawlerPerform(appid_android='nz.co.skytv.fanpass', appid_ios='941399309', countries=countries)
    # t1 = threading.Thread(target=test.get_appstore)
    # # t2 = threading.Thread(target=test.get_googleplay)
    # t1.start()
    # # t2.start()
    # t1.join()
    # # t2.join()
    # print(test.resp_ios)
    # ios_data = FrozenJson(test.resp_ios)
    # android_data = FrozenJson(test.resp_android)
    #
    # print(test.resp_android)
    # us_data = android_data.nz
    # us_data_ios = ios_data.nz

    # for i in range(len(us_data)):
    #     print('*'*20)
    #     print('reivewID: ', us_data[i].reviewId)
    #     print('username: ', us_data[i].userName)
    #     print('titel: ', ' '.join(us_data[i].content.split(' ')[0:4]))
    #     print('content: ', us_data[i].content)
    #     print('rating: ', us_data[i].score)
    #     print('version: ', us_data[i].reviewCreatedVersion)
    #     print('time: ', us_data[i].at)
    #
    # for page in range(len(us_data_ios)):
    #     try:
    #         content = us_data_ios[page].feed.entry
    #     except AttributeError:
    #         break
    #     for i in range(len(content)):
    #         print('*'*20)
    #         print('reviewId: ', content[i].id.label)
    #         print('author: ', content[i].author.name.label)
    #         print('rating: ', getattr(content[i], 'im:rating').label)
    #         print('title: ', content[i].title.label)
    #         print('content: ', content[i].content.label)
    #         print('version: ', getattr(content[i], 'im:version').label)
    #         print('time: ', us_data_ios[page].feed.updated.label)

