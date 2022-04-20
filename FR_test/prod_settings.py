from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent

with open(BASE_DIR / 'secrets.json', 'rt') as s:
    secrets = json.load(s)

DEBUG = False

ALLOWED_HOSTS = ["127.0.0.1", "localhost", "77.223.97.240"]  # изменить соответственно ip сервера

STATIC_ROOT = BASE_DIR / 'static'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': secrets['DB_NAME'],
        'HOST': secrets['DB_HOST'],
        'PORT': secrets['DB_PORT'],
        'USER': secrets['DB_USER'],
        'PASSWORD': secrets['DB_PASSWORD'],
    }
}


REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ]
}
