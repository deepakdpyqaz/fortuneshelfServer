"""
Django settings for fortuneshelf project.

Generated by 'django-admin startproject' using Django 3.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
import os
from dotenv import load_dotenv
import logging

load_dotenv() 
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-h*3*bkdxfh-sm#6(om$q5!f5jx!cp0vkty+8tuw_ugsv9y(hxm'

# SECURITY WARNING: don't run with debug turned on in production!
if os.getenv("environment")=="dev":
    DEBUG = True
else:
    DEBUG = False
ALLOWED_HOSTS = ["app.fortuneshelf.com","fortuneshelf-load-balancer-1472405162.us-east-1.elb.amazonaws.com","localhost","127.0.0.1","192.168.43.190","192.168.3.242"]


# Application definition

INSTALLED_APPS = [
    'payment.apps.PaymentConfig',
    'manager.apps.ManagerConfig',
    'order.apps.OrderConfig',
    'book.apps.BookConfig',
    'user.apps.UserConfig',
    'home.apps.HomeConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'rest_framework',
     'corsheaders',
     'schedular.apps.SchedularConfig'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'fortuneshelf.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,"templates")],
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
]

WSGI_APPLICATION = 'fortuneshelf.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv("DB_NAME"),
        'HOST': os.getenv("DB_HOST"), 
        'PORT': os.getenv("DB_PORT"), 
        'USER': os.getenv("DB_USER"),
        'PASSWORD': os.getenv("DB_PASSWORD"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
USE_S3 = not DEBUG  or True
# AWS
AWS_ACCESS_KEY_ID = os.getenv("AWSAccessKeyId")
AWS_SECRET_ACCESS_KEY = os.getenv("AWSSecretKey")
REGION_NAME = os.getenv("region_name")
if USE_S3:
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    AWS_DEFAULT_ACL = 'public-read'
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
    AWS_LOCATION = 'static'
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/'
    STATICFILES_STORAGE = 'fortuneshelf.storage_backends.StaticStorage'
      # s3 public media settings
    PUBLIC_MEDIA_LOCATION = 'media'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{PUBLIC_MEDIA_LOCATION}/'
    DEFAULT_FILE_STORAGE = 'fortuneshelf.storage_backends.PublicMediaStorage'
else:
    STATIC_URL = '/static/'

    STATIC_ROOT=os.path.join(BASE_DIR,"assets")

    STATICFILES_DIRS=[
        os.path.join(BASE_DIR,"static")
    ]
    MEDIA_ROOT=os.path.join(BASE_DIR,"media")
    MEDIA_URL="http://localhost:8000/media/"


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field


# Media setup


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS
CORS_ORIGIN_ALLOW_ALL = False
CORS_ORIGIN_WHITELIST = (
  'http://localhost:3000',
  'http://localhost:5000',
  'http://192.168.43.190:3000',
  'http://192.168.3.242:3000',
  "https://www.fortuneshelf.com",
  "http://www.fortuneshelf.com",
  "https://fortuneshelf.com",
  "http://fortuneshelf.com"
)


# EMAIL
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_MAIL")



# REST FRAMEWORK
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
}

# NIMBUS 
NP_API_KEY = os.getenv("NP_API_KEY")


# PAYU
MERCHANT_KEY=os.getenv("MERCHANT_KEY")
MERCHANT_SALT = os.getenv("MERCHANT_SALT")
SURL = os.getenv("SURL")
FURL = os.getenv("FURL")
CURL = os.getenv("CURL")
RURL = os.getenv("RURL")


# Schedular
SCHEDULAR = bool(os.getenv("SCHEDULAR"))

LOGGER=True

if DEBUG:
    level = logging.DEBUG
else:
    level = logging.ERROR
# LOGGER
if LOGGER:
    logging.basicConfig(filename='fortuneshelf.log', level=level,format='%(levelname)s:%(asctime)s %(message)s')

SUPPORT_MAIL = os.getenv("SUPPORT_MAIL")
DEVELOPER_EMAIL = os.getenv("DEVELOPER_EMAIL")
