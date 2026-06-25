import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')

# ==========================================================
# CONFIGURAÇÃO PRINCIPAL
# ==========================================================

SECRET_KEY = os.getenv('SECRET_KEY', 'dev-only-msn-reborn-secret-key-change-in-production')
DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv(
        'ALLOWED_HOSTS',
        '127.0.0.1,localhost,backend,frontend,.pythonanywhere.com',
    ).split(',')
    if host.strip()
]

APP_ENV = os.getenv('APP_ENV', 'local')

LOCAL_FRONTEND_URL = os.getenv('LOCAL_FRONTEND_URL', 'http://127.0.0.1:5173')
LOCAL_SPOTIFY_REDIRECT_URI = os.getenv(
    'LOCAL_SPOTIFY_REDIRECT_URI',
    'http://127.0.0.1:8000/api/spotify/callback/',
)

PRODUCTION_FRONTEND_URL = os.getenv('PRODUCTION_FRONTEND_URL', 'https://msn-reborn-ochre.vercel.app')
PRODUCTION_SPOTIFY_REDIRECT_URI = os.getenv(
    'PRODUCTION_SPOTIFY_REDIRECT_URI',
    'https://emanuelangelo1992.pythonanywhere.com/api/spotify/callback/',
)

if APP_ENV == 'production':
    FRONTEND_URL = os.getenv('FRONTEND_URL', PRODUCTION_FRONTEND_URL)
    SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI', PRODUCTION_SPOTIFY_REDIRECT_URI)
else:
    FRONTEND_URL = os.getenv('FRONTEND_URL', LOCAL_FRONTEND_URL)
    SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI', LOCAL_SPOTIFY_REDIRECT_URI)


# ==========================================================
# APPS
# ==========================================================

INSTALLED_APPS = [
    'daphne',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'corsheaders',

    'rest_framework',
    'rest_framework.authtoken',
    'drf_spectacular',
    'channels',

    'msn',
]


# ==========================================================
# MIDDLEWARE
# ==========================================================

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


# ==========================================================
# URLS / ASGI / WSGI
# ==========================================================

ROOT_URLCONF = 'core.urls'
ASGI_APPLICATION = 'core.asgi.application'
WSGI_APPLICATION = 'core.wsgi.application'


# ==========================================================
# TEMPLATES
# ==========================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# ==========================================================
# BANCO DE DADOS
# ==========================================================

if os.getenv('DATABASE_URL'):
    import dj_database_url

    DATABASES = {
        'default': dj_database_url.config(
            default=os.getenv('DATABASE_URL'),
            conn_max_age=600,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.getenv('SQLITE_PATH', str(BASE_DIR / 'db.sqlite3')),
        }
    }


# ==========================================================
# USUÁRIO CUSTOMIZADO
# ==========================================================

AUTH_USER_MODEL = 'msn.User'


# ==========================================================
# VALIDAÇÃO DE SENHA
# ==========================================================

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


# ==========================================================
# LOCALIZAÇÃO
# ==========================================================

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Fortaleza'
USE_I18N = True
USE_TZ = True


# ==========================================================
# STATIC / MEDIA
# ==========================================================

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ==========================================================
# DJANGO REST FRAMEWORK
# ==========================================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
}


# ==========================================================
# DOCUMENTAÇÃO DA API
# ==========================================================

SPECTACULAR_SETTINGS = {
    'TITLE': 'MSN Reborn API',
    'DESCRIPTION': 'API REST do MVP inspirado no antigo MSN: autenticação, perfil, contatos, conversas, mensagens, presença e Spotify.',
    'VERSION': '0.2.0',
    'SERVE_INCLUDE_SCHEMA': False,
}


# ==========================================================
# CORS / CSRF
# ==========================================================

_default_cors = (
    'http://127.0.0.1:5173,http://localhost:5173,'
    'http://127.0.0.1:8080,http://localhost:8080,'
    'https://msn-reborn-ochre.vercel.app'
)

CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv('CORS_ALLOWED_ORIGINS', _default_cors).split(',')
    if origin.strip()
]

CORS_ALLOWED_ORIGIN_REGEXES = [
    r'^https://.*\.vercel\.app$',
]

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv('CSRF_TRUSTED_ORIGINS', _default_cors).split(',')
    if origin.strip()
]

CORS_ALLOW_CREDENTIALS = False

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'


# ==========================================================
# CHANNELS
# ==========================================================

REDIS_URL = os.getenv('REDIS_URL', '')

if REDIS_URL:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                'hosts': [REDIS_URL],
            },
        },
    }
else:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        },
    }


# ==========================================================
# SPOTIFY
# ==========================================================

SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID', '')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET', '')
SPOTIFY_SCOPES = [
    'user-read-currently-playing',
    'user-read-playback-state',
    'user-read-private',
]
