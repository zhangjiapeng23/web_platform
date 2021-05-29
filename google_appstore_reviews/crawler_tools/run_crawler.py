import datetime
import time
import threading

from google_appstore_reviews.crawler_tools.register_crawler import registered_project

def main(hour, minute, model):
    '''
    :param hour: each day run hour
    :param minute: each day run minute
    :param model: support two modal, 'forever' and 'once'
    :return:
    '''
    for pro in registered_project():
        pro.run()

    if model == 'forever':
        while True:
            while True:
                now = datetime.datetime.now()

                if now.hour == hour and now.minute == minute:
                    break
                else:
                    time.sleep(60)

            for pro in registered_project():
                pro.run()
            time.sleep(60)


def crawler_start(hour=0, minute=0, model='once'):
    t = threading.Thread(target=main, kwargs={'hour': hour,
                                              'minute': minute,
                                              'model': model})
    t.start()


if __name__ == '__main__':
    crawler_start(hour=18, minute=24, model='once')
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

