#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/3/2

import sys
import os
import re


def main():
    apk_dir = sys.argv[1]
    apks = os.listdir(apk_dir)
    for apk in apks:
        rename(apk_dir, apk)

    new_apks = os.listdir(apk_dir)
    print(new_apks)


def rename(apk_dir, origin_name):
    prod_re = re.compile(r".*-prod-sib-release.*")
    dev_re = re.compile(r".*-dev-sib-release.*")
    protest_re = re.compile(r".*-protest-sib-release.*")
    amazon_re = re.compile(r".*-amazon-sib-release.*")
    prod_apk = 'nba_domestic.apk'
    dev_apk = 'nba_domestic_qa.apk'
    protest_apk = 'nba_domestic_charles_proxy_enabled.apk'
    amazon_apk = 'nba_domestic_amazon.apk'

    src = os.path.join(apk_dir, origin_name)
    if prod_re.match(origin_name):
        dst = os.path.join(apk_dir, prod_apk)
    elif dev_re.match(origin_name):
        dst = os.path.join(apk_dir, dev_apk)
    elif protest_re.match(origin_name):
        dst = os.path.join(apk_dir, protest_apk)
    elif amazon_re.match(origin_name):
        dst = os.path.join(apk_dir, amazon_apk)
    else:
        dst = src

    if dst != src:
        os.rename(src, dst)


if __name__ == '__main__':
    main()
