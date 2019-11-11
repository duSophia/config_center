# -*- coding: utf-8 -*-

import logging

import redis
from flask import Flask, request, jsonify
from sqlalchemy import desc

from . import settings
from .decorators import response_wrapper
from .models import session, MConfRecord, MConfEnv

app = Flask('conf_server')
REDIS_CHANNEL = 'conf_server.%s'
app.secret_key = settings.SECRET_KEY

redis_client = redis.StrictRedis(**settings.REDIS_CONF)
logger = logging.getLogger(__name__)


@app.route('/envs', methods=['GET'])
@response_wrapper
def get_envs():
    envs = [dict(name=m_env.name, display_name=m_env.display_name)
            for m_env in session.query(MConfEnv).order_by(MConfEnv.create_at).all()]
    return dict(envs=envs)


@app.route('/confs/<env>', methods=['GET'])
@response_wrapper
def get_conf(env):
    confs = session.query(MConfRecord).filter_by(env=str(env)).order_by(desc(MConfRecord.update_at)).all()
    return [dict(id=conf.id, key=conf.key, value=conf.value, update_at=conf.update_at) for conf in confs]


@app.route('/confs/<env>', methods=['POST'])
@response_wrapper
def post_confs(env):
    data = request.get_json(force=True)
    if session.query(session.query(MConfRecord).filter(
            MConfRecord.env == env, MConfRecord.key == data['key']).exists()).scalar():
        raise APIException(601, "%s 已经存在, 不能新增" % data['key'])
    if not data['key'] or not data['value']:
        raise APIException(601, "key和value不能为空")
    if '=' in data['key']:
        raise APIException(601, "key当中不能出现=")
    if ' ' in data['key']:
        raise APIException(601, "key当中不能出现空格")
    m_env = MConfEnv(name=env, display_name=env)
    m_conf = MConfRecord(key=data['key'], value=data['value'], env=env)
    session.add(m_env)
    session.add(m_conf)
    session.commit()
    publish_to_client(env, m_conf.key, m_conf.value)
    return dict(id=m_conf.id)


@app.route('/confs/<env>/<id>', methods=['PUT'])
@response_wrapper
def put_conf(env, id):
    data = request.get_json(force=True)
    if not data['value']:
        raise APIException(601, "value不能为空.")
    m_conf = session.query(MConfRecord).filter_by(id=id, env=env).first()
    if data['value'] == m_conf.value:
        raise APIException(601, "value相同就不要改了吧.")
    m_conf.value = data['value']
    session.commit()
    publish_to_client(env, m_conf.key, m_conf.value)
    return dict(id=m_conf.id)


@app.route('/<env>/cur_conn', methods=['GET'])
@response_wrapper
def get_cur_conn(env):
    env = REDIS_CHANNEL % env
    result = redis_client.execute_command("pubsub NUMSUB %s" % env)
    return dict(cur_conn=int(result[1]))


@app.route('/confs/<env>/<id>', methods=['DELETE'])
@response_wrapper
def delete_conf(env, id):
    m_conf = session.query(MConfRecord).filter_by(id=id, env=env).first()
    session.delete(m_conf)
    session.commit()
    delete_client_conf(env, m_conf.key)
    return {}


@app.teardown_request
def remove_session(*args, **kwargs):
    session.remove()


def publish_to_client(env, key, value):
    redis_client.publish(REDIS_CHANNEL % env, key + '=' + value)


def delete_client_conf(env, key):
    redis_client.publish(REDIS_CHANNEL % env, key + '=')


class APIException(Exception):
    def __init__(self, status, msg=None):
        self.status = status
        self.msg = msg


@app.errorhandler(APIException)
def hand_api_exception(exception):
    response = jsonify(dict(msg=str(exception.msg), status=exception.status))
    return response
