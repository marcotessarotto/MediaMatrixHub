"""
Django settings for mediamatrixhub project.

Generated by 'django-admin startproject' using Django 5.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import locale
import os
from pathlib import Path
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles/')

STATICFILES_DIRS = (str(BASE_DIR.joinpath('static')),)

STATIC_URL = '/static/'

# Set up django-environ
env = environ.Env(
    # Default values for variables if not set
    DEBUG=(bool, False)
)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))


SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=False)

ALLOWED_HOSTS = env('ALLOWED_HOSTS').split(',')

RECAPTCHA_PRIVATE_KEY = env('RECAPTCHA_PRIVATE_KEY')
RECAPTCHA_PUBLIC_KEY = env('RECAPTCHA_PUBLIC_KEY')

RECAPTCHA_REQUIRED_SCORE = 0.85

MEDIA_ROOT = '/opt/media/MediaMatrixHub/media/'
MEDIA_URL = '/media/'

BASE_URL = env('BASE_URL')

FROM_EMAIL = env('FROM_EMAIL')
SUBJECT_EMAIL = env('SUBJECT_EMAIL')
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env('EMAIL_PORT')
DEBUG_EMAIL = env('DEBUG_EMAIL')

MONITOR_EMAIL_ADDRESSES = env('MONITOR_EMAIL_ADDRESSES').split(',')

REGISTRATION_URL = env('REGISTRATION_URL')
VIDEOTECA_URL = env('VIDEOTECA_URL')

# CKEditor 5 settings

customColorPalette = [
        {
            'color': 'hsl(4, 90%, 58%)',
            'label': 'Red'
        },
        {
            'color': 'hsl(340, 82%, 52%)',
            'label': 'Pink'
        },
        {
            'color': 'hsl(291, 64%, 42%)',
            'label': 'Purple'
        },
        {
            'color': 'hsl(262, 52%, 47%)',
            'label': 'Deep Purple'
        },
        {
            'color': 'hsl(231, 48%, 48%)',
            'label': 'Indigo'
        },
        {
            'color': 'hsl(207, 90%, 54%)',
            'label': 'Blue'
        },
    ]

# CKEDITOR_5_CUSTOM_CSS = '/static/css/ckeditor_custom.css' # optional
# CKEDITOR_5_FILE_STORAGE = 'content/ckeditor/' #"path_to_storage.CustomStorage" # optional
CKEDITOR_5_CONFIGS = \
  {
    'default': {
        'height': '900px',
        'width': '1200px',
        'toolbar': ['heading', '|', 'bold', 'italic', 'link',
                    'bulletedList', 'numberedList', 'blockQuote', 'imageUpload', ],

    },
    'extends': {
        'blockToolbar': [
            'paragraph', 'heading1', 'heading2', 'heading3',
            '|',
            'bulletedList', 'numberedList',
            '|',
            'blockQuote',
        ],
        'toolbar': ['heading', '|', 'outdent', 'indent', '|', 'bold', 'italic', 'link', 'underline', 'strikethrough',
        'code','subscript', 'superscript', 'highlight', '|', 'codeBlock', 'sourceEditing', 'insertImage',
                    'bulletedList', 'numberedList', 'todoList', '|',  'blockQuote', 'imageUpload', '|',
                    'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', 'mediaEmbed', 'removeFormat',
                    'insertTable',],
        'image': {
            'toolbar': ['imageTextAlternative', '|', 'imageStyle:alignLeft',
                        'imageStyle:alignRight', 'imageStyle:alignCenter', 'imageStyle:side',  '|'],
            'styles': [
                'full',
                'side',
                'alignLeft',
                'alignRight',
                'alignCenter',
            ]

        },
        'table': {
            'contentToolbar': [ 'tableColumn', 'tableRow', 'mergeTableCells',
            'tableProperties', 'tableCellProperties' ],
            'tableProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            },
            'tableCellProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            }
        },
        'heading' : {
            'options': [
                { 'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph' },
                { 'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1' },
                { 'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2' },
                { 'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3' }
            ]
        }
    },
    'list': {
        'properties': {
            'styles': 'true',
            'startIndex': 'true',
            'reversed': 'true',
        }
    },
  }



# CKEDITOR_UPLOAD_PATH = 'content/ckeditor/'
# CKEDITOR_IMAGE_BACKEND = 'pillow'


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_jinja',
    'django_ckeditor_5',
    'mediaelementjs',
    'core',
    'registration',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mediamatrixhub.urls'

TEMPLATE_DIRS = [
    os.path.join(BASE_DIR, 'core/templates/'),
    os.path.join(BASE_DIR, 'registration/templates/'),
]

KEEP_DJANGO_TEMPLATES = ['admin', ]


TEMPLATES = [
    {
        'NAME': 'django',
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates/django')],  # Update this path as needed
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
    {
        'NAME': 'jinja2',
        "BACKEND": "django_jinja.backend.Jinja2",
        'DIRS': [os.path.join(BASE_DIR, 'templates/jinja2'),
                 os.path.join(BASE_DIR, 'core/templates/'),
                 os.path.join(BASE_DIR, 'registration/templates/')
                 ],  # Update this path as needed
        'APP_DIRS': True,
        'OPTIONS': {
            'environment': 'core.jinja2.JinjaEnvironment',
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ],
            "debug": True,
        },
    },
]

WSGI_APPLICATION = 'mediamatrixhub.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# generate sql script to create database and user with generate_sql_script.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST', default='127.0.0.1'),  # default to localhost if DB_HOST is not set
        'PORT': env('DB_PORT', default='3306'),  # default to 3306 if DB_PORT is not set
        'AUTOCOMMIT': True,
        'OPTIONS': {'charset': 'utf8mb4',
                    'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"},
        # https://code.djangoproject.com/ticket/18392
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'it-it'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Make sure your session cookies are persistent, not session-limited.
# By default, Django's session cookies are set to expire when the user's browser is closed.
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

SESSION_COOKIE_AGE = 1209600*2  # 4 weeks, in seconds

