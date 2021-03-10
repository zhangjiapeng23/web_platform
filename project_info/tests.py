import os

import requests
from django.test import TestCase

# Create your tests here.


def test_android_upload_api():
    android_build = os.path.join(os.path.dirname(__file__), 'testdata', 'Android_build_info.json')
    with open(android_build, 'r', encoding='utf-8') as fp:
        data = fp.read()

    # print(type(data))
    headers = {'Content-Type': 'application/json'}
    res = requests.post("http://127.0.0.1:50001/NLAndroid/",
                        headers=headers, data=data)
    print(res.status_code)

def test_ios_upload_api():
    ios_build = os.path.join(os.path.dirname(__file__), 'testdata', 'iOS_build_info.json')
    with open(ios_build, 'r', encoding='utf-8') as fp:
        data = fp.read()

    headers = {'Content-Type': 'application/json'}
    res = requests.post("http://127.0.0.1:50001/NLiOS/",
                        headers=headers, data=data)
    print(res.status_code)

def test_android_mapping_upload_api():
    mapping_file = os.path.join(os.path.dirname(__file__), 'testdata', 'mapping.txt')
    files = {'file': ('mapping.txt', open(mapping_file, 'rb'))}
    res = requests.post("http://127.0.0.1:50001/NLAndroid/upload/", files=files)
    print(res.status_code)




