from abc import ABCMeta, abstractmethod
import ssl
from collections import defaultdict
from google_play_scraper import reviews, Sort
import aiohttp
import asyncio

ssl._create_default_https_context = ssl._create_unverified_context


class Crawler(metaclass=ABCMeta):

    @abstractmethod
    def request_data(self):
        """
        implement data request method

        """
        raise NotImplemented


class GoogleCrawler(Crawler):

    def __init__(self, country, appid, max_pre_page, max_page=5):
        self.country = country
        self.appid = appid
        self.max_pre_page = max_pre_page
        self.continuation_token = None
        self.max_page = max_page

    def request_data(self):
        resp = list()
        page = 1
        while page <= self.max_page:
            if not self.continuation_token:
                res, self.continuation_token = reviews(
                    app_id=self.appid,
                    lang='en',  # defaults to 'en'
                    country=self.country,  # defaults to 'us'
                    sort=Sort.MOST_RELEVANT,  # defaults to Sort.MOST_RELEVANT
                    count=self.max_pre_page,  # defaults to 100
                    filter_score_with=None,  # defaults to None(means all score)
                )
            else:
                res, self.continuation_token = reviews(
                    app_id=self.appid,
                    continuation_token=self.continuation_token,
                )
            print('Android->page:{}, country:{}'.format(page, self.country))
            resp.extend(res)
            page += 1
        return resp



class AppStoreCrawler(Crawler):
    url = 'https://itunes.apple.com/rss/customerreviews/page={}/id={}/sortby=mostrecent/json?l=en&&cc={}'

    def __init__(self, appid, country, max_page=10):
        self.appid = appid
        self.country = country
        self.max_page = max_page

    async def request_data(self):
        resp_dict = defaultdict(list)
        page = 1
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            while page <= self.max_page:
                url = self.url.format(page, self.appid, self.country)
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json(content_type=None)
                        resp_dict[self.country].append(data)
                        print('iOS->page: {}, country:{}'.format(page, self.country))
                    page += 1

            return resp_dict





if __name__ == '__main__':
    appid = 'com.nbaimd.gametime.nba2011'
    appid_iOS = '484672289'
    countrys = ['us', 'au', 'nz', 'ch']
    # start = dict()
    # for country in countrys:
    #     start[country] = GoogleCrawler(appid=appid, max_pre_page=50, country=country, page=10)
    # print(start)
    # res = defaultdict(list)
    # for k,v in start.items():
    #     for resp in v.request_data():
    #         res[k].append(resp)
    # print(res)
    # print('us date nums: ', len(res['us']))
    # print('AU date nums: ', len(res['au']))

    # iOS

    async def main():
        start = dict()
        resp = dict()
        for country in countrys:
            start[country] = AppStoreCrawler(appid=appid_iOS, max_page=10, country=country)
        # for country, request in start.items():
        #    await request.request_data()
        #    resp[country] = res
        to_do_country = [country for country in start.keys()]
        to_do = [start[country].request_data() for country in to_do_country ]
        to_do_iter = asyncio.as_completed(to_do)
        for country, future in zip(to_do_country, to_do_iter):
            res = await future
            resp[country] = res

        # print(resp)




        # msg = '{}: {}'
        # for k,v in resp.items():
        #     print(msg.format(k, v))
        #     print(len(v))




    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
