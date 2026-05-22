from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ==========================================================
# CONFIGURAÇÃO PRINCIPAL
# ==========================================================
# MVP em desenvolvimento. Antes de produção real, troque DEBUG para False
# e mova SECRET_KEY / SPOTIFY_CLIENT_SECRET para variáveis de ambiente.

SECRET_KEY = 'dev-only-msn-reborn-secret-key'
DEBUG = True

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    'emanuelangelo1992.pythonanywhere.com',
    '.pythonanywhere.com',
]

# Ambiente ativo do projeto.
# Use 'local' para rodar na sua máquina.
# Use 'production' para backend no PythonAnywhere e frontend na Vercel.
APP_ENV = 'production'

LOCAL_FRONTEND_URL = 'http://127.0.0.1:5173'
LOCAL_BACKEND_API_URL = 'http://127.0.0.1:8000/api'
LOCAL_WS_URL = 'ws://127.0.0.1:8000'
LOCAL_SPOTIFY_REDIRECT_URI = 'http://127.0.0.1:8000/api/spotify/callback/'

PRODUCTION_FRONTEND_URL = 'https://msn-reborn-ochre.vercel.app'
PRODUCTION_BACKEND_API_URL = 'https://emanuelangelo1992.pythonanywhere.com/api'
PRODUCTION_WS_URL = 'wss://emanuelangelo1992.pythonanywhere.com'
PRODUCTION_SPOTIFY_REDIRECT_URI = 'https://emanuelangelo1992.pythonanywhere.com/api/spotify/callback/'

if APP_ENV == 'production':
    FRONTEND_URL = PRODUCTION_FRONTEND_URL
    SPOTIFY_REDIRECT_URI = PRODUCTION_SPOTIFY_REDIRECT_URI
else:
    FRONTEND_URL = LOCAL_FRONTEND_URL
    SPOTIFY_REDIRECT_URI = LOCAL_SPOTIFY_REDIRECT_URI


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

MIDDLEWARE = [
    # Precisa ficar no topo para responder corretamente o preflight CORS.
    'corsheaders.middleware.CorsMiddleware',

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'
ASGI_APPLICATION = 'core.asgi.application'
WSGI_APPLICATION = 'core.wsgi.application'

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

# Desenvolvimento: SQLite. Futuro: trocar ENGINE para django.db.backends.postgresql.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_USER_MODEL = 'msn.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Fortaleza'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'MSN Reborn API',
    'DESCRIPTION': 'API REST do MVP inspirado no antigo MSN: autenticação, perfil, contatos, conversas, mensagens, presença e Spotify.',
    'VERSION': '0.1.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# ==========================================================
# CORS / CSRF
# ==========================================================

CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "https://msn-reborn-ochre.vercel.app",
]

CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.vercel\.app$",
]

CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "https://msn-reborn-ochre.vercel.app",
    "https://emanuelangelo1992.pythonanywhere.com",
]

CORS_ALLOW_CREDENTIALS = False

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

# ==========================================================
# SPOTIFY
# ==========================================================
# 1. No Spotify Developer Dashboard, cadastre as duas Redirect URIs:
#    - http://127.0.0.1:8000/api/spotify/callback/
#    - https://emanuelangelo1992.pythonanywhere.com/api/spotify/callback/
# 2. Cole seu Client Secret real abaixo apenas no seu ambiente local/servidor.
# 3. Nunca suba Client Secret real para repositório público.

SPOTIFY_CLIENT_ID = '49483fb723b942f48c3cf1aa25d8be96'
SPOTIFY_CLIENT_SECRET = '91735089a4c445df825036adee4d207c'
SPOTIFY_SCOPES = [
    'user-read-currently-playing',
    'user-read-playback-state',
    'user-read-private',
]
