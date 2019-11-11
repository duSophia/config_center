# -*- coding: utf-8 -*-
import logging
import os
import sys
import time
import unittest

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(base_dir))

from conf.client.api import ConfClient, get_conf_decorator

logging.basicConfig(handlers=[logging.StreamHandler()], level=logging.INFO)

conf_client = ConfClient('127.0.0.1:8888', 'JTPay')
conf_decorator = get_conf_decorator(conf_client)


@conf_decorator(key='channel_pay')
class AppConf(object):
    mch_666002 = {
        "API_KEY": "9527",
        "GET_WAY": "http://www.google.com"
    }


print('6666666 ', AppConf.mch_666002)


class ClientTestCase(unittest.TestCase):
    @staticmethod
    def test_get_value():
        for i in range(5):
            print("=====>", conf_client.get('test'))
            time.sleep(3)

    @staticmethod
    def test_get_by_decorator():
        for i in range(5):
            print('=====> ', AppConf.mch_666002['API_KEY'], AppConf.mch_666002['GET_WAY'])
            time.sleep(3)


if __name__ == '__main__':
    unittest.main()
