import os

PROJECT_DIR = os.path.dirname(__file__)
BASE_DIR = PROJECT_DIR  # setting present in new startproject


INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'systemjs',
    'tests.app',
]

ROOT_URLCONF = 'tests.urls'

DEBUG = False
STATIC_URL = '/static/'
SECRET_KEY = 'this-is-really-not-a-secret'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_DIR, 'database.db'),
    }
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': [
            os.path.join(PROJECT_DIR, 'templates'),
        ],
        'OPTIONS': {
            'context_processors': [
                "django.template.context_processors.i18n",
            ],
        },
    },
]

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')
