import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
import dj_database_url
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-me-in-production')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
if not DEBUG and (len(SECRET_KEY) < 50 or SECRET_KEY.startswith(('django-insecure-', 'replace-', 'your-secret'))):
    raise ImproperlyConfigured('Set a private SECRET_KEY before disabling DEBUG')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'accounts',
    'solver',
    'datasets',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'math_project.urls'

TEMPLATES = [{'BACKEND': 'django.template.backends.django.DjangoTemplates',
               'DIRS': [], 'APP_DIRS': True,
               'OPTIONS': {'context_processors': [
                   'django.template.context_processors.request',
                   'django.contrib.auth.context_processors.auth',
                   'django.contrib.messages.context_processors.messages',
               ]}}]

WSGI_APPLICATION = 'math_project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
if os.environ.get('DATABASE_URL'):
    DATABASES['default'] = dj_database_url.parse(os.environ['DATABASE_URL'], conn_max_age=0)
elif not DEBUG:
    raise ImproperlyConfigured('Production requires DATABASE_URL (PostgreSQL)')
if not DEBUG and DATABASES['default']['ENGINE'] != 'django.db.backends.postgresql':
    raise ImproperlyConfigured('Production requires PostgreSQL')

# The candidate is selected explicitly. An empty value disables ML inference.
ML_MODEL_PATH = os.environ.get('ML_MODEL_PATH', '')
ML_CONFIDENCE_THRESHOLD = float(os.environ.get('ML_CONFIDENCE_THRESHOLD', '0.60'))
ML_CONFIDENCE_MARGIN = float(os.environ.get('ML_CONFIDENCE_MARGIN', '0.15'))

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Skopje'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Media files (uploaded images/PDFs stored here temporarily)
MEDIA_URL = '/media/'
MEDIA_ROOT = PROJECT_ROOT / 'data' / 'uploads'
STATIC_ROOT = BASE_DIR / 'staticfiles'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': True,
}

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3001',
    'http://127.0.0.1:3001',
]
CORS_ALLOW_CREDENTIALS = True

# The solver uses the Responses API. The default is a balanced reasoning model;
# choose another supported model through the environment when benchmarking.
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-5.6-terra')
OPENAI_REASONING_EFFORT = os.environ.get('OPENAI_REASONING_EFFORT', 'medium')
OPENAI_MAX_OUTPUT_TOKENS = int(os.environ.get('OPENAI_MAX_OUTPUT_TOKENS', '3500'))
OPENAI_TIMEOUT_SECONDS = float(os.environ.get('OPENAI_TIMEOUT_SECONDS', '45'))
CHAT_HISTORY_CHAR_LIMIT = 12000
CHAT_MEMORY_CHAR_LIMIT = 3000
DATA_UPLOAD_MAX_MEMORY_SIZE = 15000000

# Public signup must be disabled when this is hosted for invited testers. The
# current local-development default keeps the existing registration screen usable.
ALLOW_PUBLIC_REGISTRATION = os.environ.get('ALLOW_PUBLIC_REGISTRATION', 'true' if DEBUG else 'false').lower() == 'true'
TESSERACT_PATH   = os.environ.get('TESSERACT_PATH', r'C:\Program Files\Tesseract-OCR\tesseract.exe')
