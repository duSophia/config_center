# -*- coding: utf-8 -*-

from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.engine.url import URL as AlchemyURL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from conf.server.settings import sqlchemy_db

engine = create_engine("%s?charset=utf8mb4" % AlchemyURL(**sqlchemy_db), pool_recycle=3600)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = scoped_session(Session)
ModelBase = declarative_base()


class MConfRecord(ModelBase):
    __tablename__ = 'conf_record'

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(128))
    value = Column(Text())

    env = Column(String(12), ForeignKey('conf_env.name'))

    create_at = Column(DateTime, default=datetime.now)
    update_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    UniqueConstraint('env', 'key', name='uidx_env_key')


class MConfEnv(ModelBase):
    __tablename__ = 'conf_env'

    name = Column(String(12), primary_key=True)
    display_name = Column(String(24))

    create_at = Column(DateTime, default=datetime.now())


def clear_schema():
    """删除所有数据表"""
    ModelBase.metadata.drop_all(engine)


def init_schema():
    """新建所有数据表"""
    ModelBase.metadata.create_all(engine)


if __name__ == "__main__":
    init_schema()
