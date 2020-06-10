# -*- coding: utf-8 -*-

import os


BASEDIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """base config"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sharp'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class DevelopmentConfig(Config):
    DEBUG = True

    REDIS_HOST = '127.0.0.1'
    REDIS_PASSWORD = ''
    REDIS_PORT = 6379
    REDIS_DB = 1


class ProductionConfig(Config):
    DEBUG = False


AppConfig = {
    'development': DevelopmentConfig,
    'testing': ProductionConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
