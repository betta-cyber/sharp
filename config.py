# -*- coding: utf-8 -*-

import os
import requests


BASEDIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """base config"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sharp'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class DevelopmentConfig(Config):
    DEBUG = False

    headers = {
        "Authorization": "Bearer s.KOmCzhE0ZoTo7MltoBs0eUdS"
    }
    r = requests.get("https://10.1.161.12:8200/v1/redis/data/soc", headers=headers, verify=False)
    data = r.json()['data']['data']

    REDIS_HOST = '127.0.0.1'
    # REDIS_PASSWORD = data['password']
    REDIS_PASSWORD = ''
    REDIS_PORT = 6379
    REDIS_DB = 1

    BROWERLESS_WS = "10.1.161.29:3000"


class ProductionConfig(Config):
    DEBUG = False


AppConfig = {
    'development': DevelopmentConfig,
    'testing': ProductionConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
