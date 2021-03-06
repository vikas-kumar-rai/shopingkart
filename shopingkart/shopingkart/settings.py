
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '-w(j=gu@*^q#7#_w8s)_=a#nbd^0l!)=&htb3*_d=fmaw9_pr='

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "app",
    "social_django",
    'crispy_forms',
    'django_countries',
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

ROOT_URLCONF = 'shopingkart.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'social_django.context_processors.backends',            #added
                'social_django.context_processors.login_redirect',      #added
            ],
        },
    },
]

AUTHENTICATION_BACKENDS = (                                              #added
    'social_core.backends.facebook.FacebookOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)



WSGI_APPLICATION = 'shopingkart.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'

AUTH_USER_MODEL = 'app.CustomerRegistration'

IMAGE_DIRS = [
    os.path.join(BASE_DIR, "images")
]

LOGIN_URL = 'login'
LOGOUT_URL = 'logout'
LOGIN_REDIRECT_URL = 'home'


SOCIAL_AUTH_FACEBOOK_KEY = '2810221105761724'  # App ID
SOCIAL_AUTH_FACEBOOK_SECRET = ""



EMAIL_USE_TLS=True
EMAIL_HOST='smtp.gmail.com'
EMAIL_HOST_USER='vikaskumar.zapbuild@gmail.com'
EMAIL_PORT=587
EMAIL_HOST_PASSWORD=''

MEDIA_ROOT = os.path.join(BASE_DIR, 'images')
MEDIA_URL = '/images/'

CRISPY_TEMPLATE_PACK = 'bootstrap4'

STRIPE_SECRET_KEY = 'sk_test_tUWyyQEWDjE8YQRDfVTMhOII00XvMbehJE'
STRIPE_PUBLISHABLE_KEY = 'pk_test_7qyvzdWvNskoksO8u5u51qbn00C5mgJxcZ'
