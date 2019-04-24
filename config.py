# coding: utf-8

import os
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler

basedir = Path(__file__).parent

class Config:
    ADMINS = os.environ.get('ADMINS', '').split(',')

    BROKER_HOST = os.environ.get('BROKER_HOST', 'vps505484.ovh.net')
    BROKER_PORT = int(os.environ.get('BROKER_PORT', '1883'))
    BROKER_USERNAME = os.environ.get('BROKER_USERNAME', 'chunk_daemon')
    BROKER_PASSWORD = os.environ.get('BROKER_PASSWORD', 'chunk_daemon')

    DEVICES_WILDCARD = os.environ.get('DEVICES_WILDCARD', 'sensors/+/from_device')
    CHUNK_DIVISOR = int(os.environ.get('CHUNK_DIVISOR', '4'))

    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_SERVER = os.environ.get('MAIL_SERVER', '')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '0'))
    MAIL_SENDER = os.environ.get('MAIL_SENDER', '')
    MAIL_PREFIX = os.environ.get('MAIL_PREFIX', '[Earth Grid][Chunk daemon]')

    LOG_DIRECTORY = os.environ.get('LOG_DIRECTORY', basedir)
    LOG_PATH = os.environ.get('LOG_PATH', str(basedir / 'docker' / 'logs' / 'chunk_daemon.log'))
    LOG_SIZE = int(os.environ.get('LOG_SIZE', '20000'))
    LOG_COUNT = int(os.environ.get('LOG_COUNT', '10'))
    LOG_ENCODING = os.environ.get('LOG_ENCODING', 'utf-8')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):

    @staticmethod
    def init_app(app):
        Config.init_app(app)

        for hdler in app.logger.handlers:
            if isinstance(hdler, logging.FileHandler):
                if hdler.baseFilename == os.path.abspath(os.fspath(app.config.LOG_PATH)):
                    return

        handler = RotatingFileHandler(app.config.LOG_PATH,
                                      maxBytes=app.config.LOG_SIZE,
                                      backupCount=app.config.LOG_COUNT,
                                      encoding=app.config.LOG_ENCODING)
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        )

        handler.setFormatter(formatter)
        handler.setLevel(logging.DEBUG)

        app.logger.addHandler(handler)


class ProductionConfig(Config):

    @staticmethod
    def init_app(app):
        DevelopmentConfig.init_app(app)

        from utils.handlers import SMTPHandlerUnicode

        for hdler in app.logger.handlers:
            if type(hdler) == SMTPHandlerUnicode:
                if hdler.fromaddr == app.config.MAIL_SENDER:
                    return

        credentials = (app.config.MAIL_USERNAME, app.config.MAIL_PASSWORD)
        secure = ()

        mail_handler = SMTPHandlerUnicode(
            mailhost=(app.config.MAIL_SERVER, app.config.MAIL_PORT),
            fromaddr=app.config.MAIL_SENDER,
            toaddrs=app.config.ADMINS,
            subject=app.config.MAIL_PREFIX,
            credentials=credentials,
            secure=secure
        )

        formatter = logging.Formatter(
            '%(asctime)s -- %(name)s -- %(message)s'
        )

        mail_handler.setFormatter(formatter)

        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
