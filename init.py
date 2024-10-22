from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_caching import Cache
import redis
from config import Config
from celery import Celery
from celery.schedules import crontab


db = SQLAlchemy()

redis_client = redis.StrictRedis.from_url(Config.REDIS_URL)

cache = Cache(config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': Config.REDIS_URL,
    'CACHE_DEFAULT_TIMEOUT': 43200
})


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    db.init_app(app)
    migrate = Migrate(app, db)
    cache.init_app(app)

    return app


def make_celery(app):
    app.config['beat_schedule'] = {
        'remove_inactive_users': {
            'task': 'remove_inactive_users',
            'schedule': crontab(minute='*/5'),
        }
    }
    app.config['timezone'] = 'Europe/Minsk'

    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'],
                    backend=app.config['CELERY_RESULT_BACKEND'])
    celery.conf.update({
        'broker_url': app.config['CELERY_BROKER_URL'],
        'result_backend': app.config['CELERY_RESULT_BACKEND'],
        'beat_schedule': app.config['beat_schedule'],
        'beat_max_loop_interval': 60,
        'timezone': app.config['timezone'],
    })
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery

