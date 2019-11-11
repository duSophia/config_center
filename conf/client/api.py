# -*- coding: utf-8 -*-
import importlib
import json
import logging
import pickle
import threading

import requests
from redis import StrictRedis

logger = logging.getLogger(__name__)


class CanNotGetConfError(Exception):
    pass


class ConfInitError(Exception):
    pass


def load_callbacks(callbacks):
    """
    加载配置变更回调处理方法
    """
    callbacks_dict = {}
    if callbacks:
        assert isinstance(callbacks, dict)
        for key, full_name in callbacks.items():
            mod_path, sep, func_name = full_name.rpartition('.')
            mod = importlib.import_module(mod_path)
            func = getattr(mod, func_name)
            callbacks_dict[key] = func
    return callbacks_dict


class ConfClient:
    CACHE_FILE = '/tmp/conf_client_%s.cache'
    CONF_URL = 'http://%s/confs/%s'
    REDIS_CHANNEL = 'conf_server.%s'

    def __init__(self, server_host, env, redis_conf=None, callbacks=None):
        self.conf = {}  # 全局的配置
        self.redis_channel = self.REDIS_CHANNEL % env
        self.cache_file = self.CACHE_FILE % env
        self.conf_url = self.CONF_URL % (server_host, env)
        self.redis_conf = redis_conf or {}
        self.pubsub = None  # 主线程里面不要做危险的事情, redis初始化如果放在这里, redis服务没启动,项目就启动不了了.
        try:
            self.callbacks = load_callbacks(callbacks)
        except:
            self.callbacks = dict()
            logger.exception('load conf callbacks fail')

        try:
            self.start()
        except ConfInitError:
            logger.exception("配置中心初始化失败")
        print('=======end')

    def start(self):
        """
        启动conf client, 依次执行以下操作.
        从conf server初始化所有配置信息, 如果如果不能, 则从cache file初始化
        订阅redis, 获取配置更新.
        """
        if not self.init_conf_from_server():
            if not self.init_conf_from_cache():
                raise ConfInitError

        t = threading.Thread(target=self.subscribe)
        t.daemon = True
        t.start()

    def subscribe(self):
        """订阅redis推送"""
        try:
            self.pubsub = StrictRedis(**self.redis_conf).pubsub()
            self.pubsub.subscribe(self.redis_channel)

            logger.info('===== sub start')
            for msg in self.pubsub.listen():
                logger.info('===== sub receive')
                if msg['type'] == 'message':
                    data = msg['data'].decode()
                    logger.info('[conf] get subscribe data: %s' % data)
                    p = data.partition('=')
                    key, value = p[0], p[2]
                    if not value:
                        del self.conf[key]
                    else:
                        self.conf[key] = value
                        # 处理对应key的回调
                        if self.callbacks.get(key):
                            self.callbacks[key]()
                    self.dumps_to_cache()
            logger.info('===== sub end')
        except Exception:
            logger.exception('[conf] Unknown error occur when subscribing.')

    def init_conf_from_server(self):
        """从conf server初始化配置"""
        try:
            r = requests.get(self.conf_url)
            if r.status_code == 200:
                confs = r.json()
                print(confs)
                for conf in confs:
                    self.conf[conf['key']] = conf['value']
                logger.info('Get conf from %s, confs: %s' % (self.conf_url, self.conf))
                self.dumps_to_cache()
        except Exception:
            logger.exception('[conf] Can not init conf from server')
            return False
        return True

    def init_conf_from_cache(self):
        """从本地缓存文件恢复配置"""
        try:
            with open(self.cache_file, 'rb') as f:
                self.conf = pickle.loads(f.read())
                logger.info('[conf] Get conf from file: %s, confs: %s' % (self.cache_file, self.conf))
                return True
        except Exception:
            #  捕捉到可能出现的异常,打个exception, 不希望影响正常的push.
            logger.exception('[conf] Can not init from cache file.')

    def dumps_to_cache(self):
        """
        把当前配置缓存到cache文件
        """
        try:
            with open(self.cache_file, 'wb') as f:
                # TODO: 共用变量的地方,不加锁的危险都先cache住吧
                f.write(pickle.dumps(self.conf))
                logger.info('[conf] dump conf to file: %s, confs: %s' % (self.cache_file, self.conf))
        except Exception:
            #  捕捉到可能出现的异常,打个exception, 不希望影响正常的push.
            logger.exception('[conf] conf saved to cache file failed.')

    def get(self, key, default=None):
        """从配置中心根据key获取value, 不存在则返回默认值"""
        value = self.conf.get(key)
        if value is None and default is None:
            raise CanNotGetConfError('key: %s' % key)
        return value if value is not None else default

    def get_int(self, key, default=None):
        """从配置中心获取value, 并转化为int, 不成功返回默认值"""
        value = self.conf.get(key)
        if value is not None:
            try:
                return int(value)
            except ValueError:
                pass
        if default is None:
            raise CanNotGetConfError('key: %s' % key)
        else:
            return default

    def get_dict(self, key, default=None):
        """从配置中心获取value, 并转化为python dict, 不成功返回默认值"""
        value = self.conf.get(key)
        if value:
            try:
                return json.loads(value)
            except (ValueError, TypeError):
                pass
        if default is None:
            raise CanNotGetConfError('key: %s' % key)
        else:
            return default


def get_conf_decorator(conf):
    def conf_decorator(key):
        def wrapper(origin_class):

            def __getattribute__(self, item):
                try:
                    return conf.get_dict(key)[item]
                except (CanNotGetConfError, KeyError):
                    try:
                        return super(origin_class, self).__getattribute__(item)
                    except (KeyError, AttributeError):
                        raise CanNotGetConfError('key: %s item: %s' % (key, item))

            origin_class.__getattribute__ = __getattribute__
            return origin_class()

        return wrapper

    return conf_decorator
