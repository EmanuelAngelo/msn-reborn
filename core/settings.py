from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ==========================================================
# CONFIGURAÇÃO PRINCIPAL
# ==========================================================

SECRET_KEY = "dev-only-msn-reborn-secret-key"
DEBUG = True

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "emanuelangelo1992.pythonanywhere.com",
    ".pythonanywhere.com",
]

APP_ENV = "production"

LOCAL_FRONTEND_URL = "http://127.0.0.1:5173"
LOCAL_SPOTIFY_REDIRECT_URI = "http://127.0.0.1:8000/api/spotify/callback/"

PRODUCTION_FRONTEND_URL = "https://msn-reborn-ochre.vercel.app"
PRODUCTION_SPOTIFY_REDIRECT_URI = "https://emanuelangelo1992.pythonanywhere.com/api/spotify/callback/"

if APP_ENV == "production":
    FRONTEND_URL = PRODUCTION_FRONTEND_URL
    SPOTIFY_REDIRECT_URI = PRODUCTION_SPOTIFY_REDIRECT_URI
else:
    FRONTEND_URL = LOCAL_FRONTEND_URL
    SPOTIFY_REDIRECT_URI = LOCAL_SPOTIFY_REDIRECT_URI


# ==========================================================
# APPS
# ==========================================================

INSTALLED_APPS = [
    "daphne",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "corsheaders",

    "rest_framework",
    "rest_framework.authtoken",
    "drf_spectacular",
    "channels",

    "msn",
]


# ==========================================================
# MIDDLEWARE
# ==========================================================

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",

    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ==========================================================
# URLS / ASGI / WSGI
# ==========================================================

ROOT_URLCONF = "core.urls"
ASGI_APPLICATION = "core.asgi.application"
WSGI_APPLICATION = "core.wsgi.application"


# ==========================================================
# TEMPLATES
# ==========================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# ==========================================================
# BANCO DE DADOS
# ==========================================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# ==========================================================
# USUÁRIO CUSTOMIZADO
# ==========================================================

AUTH_USER_MODEL = "msn.User"


# ==========================================================
# VALIDAÇÃO DE SENHA
# ==========================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# ==========================================================
# LOCALIZAÇÃO
# ==========================================================

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Fortaleza"
USE_I18N = True
USE_TZ = True


# ==========================================================
# STATIC / MEDIA
# ==========================================================

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ==========================================================
# DJANGO REST FRAMEWORK
# ==========================================================

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}


# ==========================================================
# DOCUMENTAÇÃO DA API
# ==========================================================

SPECTACULAR_SETTINGS = {
    "TITLE": "MSN Reborn API",
    "DESCRIPTION": "API REST do MVP inspirado no antigo MSN: autenticação, perfil, contatos, conversas, mensagens, presença e Spotify.",
    "VERSION": "0.1.0",
    "SERVE_INCLUDE_SCHEMA": False,
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

SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"


# ==========================================================
# CHANNELS
# ==========================================================

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}


# ==========================================================
# SPOTIFY
# ==========================================================
# No Spotify Developer Dashboard, cadastre:
# - http://127.0.0.1:8000/api/spotify/callback/
# - https://emanuelangelo1992.pythonanywhere.com/api/spotify/callback/

SPOTIFY_CLIENT_ID = '49483fb723b942f48c3cf1aa25d8be96'
SPOTIFY_CLIENT_SECRET = '91735089a4c445df825036adee4d207c'
SPOTIFY_SCOPES = [
    "user-read-currently-playing",
    "user-read-playback-state",
    "user-read-private",
]