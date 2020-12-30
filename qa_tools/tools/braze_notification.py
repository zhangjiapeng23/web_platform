
import time

import requests


class BrazePush:
    platforms = ["android_push", "apple_push"]

    def __init__(self, instance_url, api_key, deeplink_scheme, test_account):
        self.__instance_url = instance_url
        self.__api_key = api_key
        self.__deeplink_scheme = deeplink_scheme
        self.test_account = test_account

    def __str__(self):
        return self.instance_url + ':' + self.api_key

    @property
    def instance_url(self):
        return self.__instance_url

    @property
    def api_key(self):
        return self.__api_key

    @property
    def deeplink_scheme(self):
        return self.__deeplink_scheme

    def __send_request(self, message, args):
        for platform in self.platforms:
            params = {"api_key": self.__api_key, "external_user_ids": self.test_account,
                    "messages": {platform: {"alert": message, "extra": args}}}
            # res = requests.post(self.__instance_url, json=params)
            print(args)

    def __send_push_notification(self, key1, value1, key2=None, value2=None, key3=None, value3=None):
        if key1 and key2 and key3:
            args = {key1: value1, key2: value2, key3: value3}
            message = 'Braze-' + key1 + ': ' + value1 + '\n' + key2 + ':' + value2 + ' - ' + key3 + ':' + value3
            self.__send_request(message, args)
            print(message + ' will send.')
        elif key1 and key2 and not key3:
            args = {key1: value1, key2: value2}
            message = 'Braze-' + key1 + ': ' + value1 + '\n' + key2 + ':' + value2
            self.__send_request(message, args)
            print(message + ' will send.')
        elif key1 and not key2 and not key3:
            args = {key1: value1}
            message = 'Braze-' + key1 + ': ' + value1
            self.__send_request(message, args)
            print(message + ' will send.')
        else:
            return 'Sending wrong test values'

        time.sleep(1)

    
    def push_by_push_type(self, param: tuple):
        '''
        EX. (1) 'GAMES', 'GAME_DATE', '04/03/2018', 'GAME_ID', '0021701156'
            (2) 'NEWS', 'NEWS_ID', news_id
            (3) 'VIDEOS', 'VIDEO_ID', video_seoname
            (4) 'PACKAGES'
        '''
        self.__send_push_notification('PUSH_TYPE', *param)

    def push_by_deeplink(self, param: str):
        deeplink = self.__deeplink_scheme + '://' + param
        self.__send_push_notification('deeplink', deeplink)
        

    def push_by_general(self, param: tuple):
        '''
            general push:
            level1 = ['type', 'section', 'section_id']
            level2 = ['id', 'content_id']
            detail page inclue: game, news, video

            EX. main page: type/sectoin/section_id: games/home/account...
                detail page: type/section/section_id: game/video. id/content_id: game_seoname/video_seoname
                special: news detail level2 only use news type/secti0n/section_id: news, newsid: news_id
        '''

        self.__send_push_notification(*param)
        
