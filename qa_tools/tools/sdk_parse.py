#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/2/16

from Crypto.Cipher import AES
import json
import requests
import base64
import urllib3

urllib3.disable_warnings()

BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s: s[0:-ord(s[-1])]


class SdkConfigParse:

    def __init__(self):
        self.issupported = ['NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO']
        self.comments = ['Not support', 'v5 Service', 'v5 Service', 'Not support', 'Not support', 'Not support',
                    'Config doesn\'t support Omniture Tracking',
                    'Config doesn\'t support Google Analyse Tracking']
        self.configdic = None
        self.text_decrypted_trim = None
        self.appid = None
        self.configurl = None
        self.targetconfignmc = None
        self.appkeyencypt = None

    def __decryp(self, nmcstring, key='NeuLionAppKeyMob'):
        encrypted_text = nmcstring
        aes = AES.new(key.encode("utf8"), AES.MODE_ECB)
        text_decrypted = str(aes.decrypt(base64.decodebytes(bytes(encrypted_text, encoding='utf8'))).decode("utf8"))
        self.text_decrypted_trim = unpad(text_decrypted)
        self.configdic = json.loads(self.text_decrypted_trim)
        return self.configdic, self.text_decrypted_trim

    def __targeturl(self):
        self.configurl = self.configdic['configUrl']
        self.appid = self.configdic['appId']
        return self.configurl, self.appid

    def __findtargetconfig(self):
        headers = dict()
        headers['User_agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) ' \
                                'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36r)'
        with requests.session() as c:
            r = c.get(self.configurl, headers=headers, verify=False)
            self.targetconfignmc = str(r.text)
        return self.targetconfignmc

    def __appkeyenc(self):
        self.appkeyencypt = (str(self.appid).upper() + 'NeuLionMobile')[0:16]
        return self.appkeyencypt

    def __funcsupport(self):
        for item in self.configdic['base']['services']:
            if item['nlid'] == 'nl.service.app':
                self.issupported[0] = 'YES'
                self.comments[0] = item['url']

            if item['nlid'] == 'nl.service.app.api':
                self.issupported[1] = 'YES'
                self.comments[1] = item['url']

            if item['nlid'] == 'nl.service.app.pcm':
                self.issupported[2] = 'YES'
                self.comments[2] = item['url']

            if item['nlid'] == 'nl.service.personalization':
                self.issupported[3] = 'YES'
                self.comments[3] = item['url']

            if item['nlid'] == 'nl.service.cast':
                self.issupported[4] = 'YES'
                self.comments[4] = item['params']['appId']

            if item['nlid'] == 'nl.service.qos':
                self.issupported[5] = 'YES'
                self.comments[5] = item['url']

            if item['nlid'] == 'nl.service.oa':
                self.issupported[6] = 'YES'
                self.comments[6] = item['params']['videoHeartBeatServer']

            if item['nlid'] == 'nl.service.gaa':
                self.issupported[7] = 'YES'
                self.comments[7] = item['params']['gaa']

    def parse(self, nmcstring):
        self.__decryp(nmcstring)
        self.__targeturl()
        self.__appkeyenc()
        self.__findtargetconfig()
        self.__decryp(self.targetconfignmc, self.appkeyencypt)
        self.__funcsupport()

