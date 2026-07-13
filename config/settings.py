"""Django settings for the Learn Morse Code backend.

Toda configuração sensível ou dependente de ambiente vem de variáveis de
ambiente (arquivo `.env` local, GitHub Secrets em CI/CD). Nunca versionar
`SECRET_KEY`, credenciais de banco ou segredos JWT.
"""

from datetime import timedelta
from pathlib import Path

import environ
from corsheaders.defaults import default_headers

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
    REDIS_URL=(str, "redis://localhost:6379/0"),
    CORS_ALLOWED_ORIGINS=(list, []),
    USE_X_FORWARDED_PROTO=(bool, False),
)

# Lê o .env se existir (em produção/CI as variáveis vêm do ambiente).
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Terceiros
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    # Apps do projeto
    "apps.accounts",
    "apps.morse",
    "apps.lessons",
    "apps.practice",
    "apps.statistics",
]

MIDDLEWARE = [
    # CorsMiddleware precisa vir antes de qualquer middleware que possa
    # gerar resposta (para incluir os headers CORS também em erros).
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "config.middleware.ContentSecurityPolicyMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

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

WSGI_APPLICATION = "config.wsgi.application"

# Banco de dados — PostgreSQL via DATABASE_URL
# ex.: postgres://morse:morse@localhost:5432/morse
DATABASES = {
    "default": env.db("DATABASE_URL"),
}
DATABASES["default"]["CONN_MAX_AGE"] = env.int("CONN_MAX_AGE", default=60)

# Cache — Redis (uso futuro: cache de configurações/lições, filas)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": env("REDIS_URL"),
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "accounts.User"

# Django REST Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    # Rate limiting global — os limites por rota de autenticação (escopo
    # "auth") continuam valendo via ScopedRateThrottle nas views.
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {
        "anon": "60/min",
        "user": "120/min",
        # Rotas de autenticação (register/login/refresh/logout) — proteção
        # contra brute force, aplicada por IP via ScopedRateThrottle.
        "auth": "10/min",
    },
}

# JWT (SimpleJWT) — access token curto; refresh token entregue via cookie
# httpOnly/Secure/SameSite=Strict (implementação na Fase 1).
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}

# Cookie httpOnly que transporta o refresh token (decisão conjunta com o
# frontend): definido no login/refresh e enviado apenas às rotas sob /api/auth.
REFRESH_TOKEN_COOKIE_NAME = "refresh_token"  # noqa: S105 — nome do cookie, não um segredo
REFRESH_TOKEN_COOKIE_PATH = "/api/auth"  # noqa: S105 — path do cookie, não um segredo

# CORS — o frontend Angular roda em outra origem e envia o cookie httpOnly
# de refresh, portanto as origens precisam ser explícitas (nunca "*") e
# credenciais habilitadas. Configurável por ambiente via CORS_ALLOWED_ORIGINS.
CORS_ALLOWED_ORIGINS = env("CORS_ALLOWED_ORIGINS")
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = (
    *default_headers,
    "x-csrf-protection",  # header de proteção CSRF das rotas de refresh/logout
)

# Content-Security-Policy (API JSON + Django admin). `frame-ancestors 'none'`
# reforça o X-Frame-Options; 'unsafe-inline' em style-src é exigido pelo admin.
CONTENT_SECURITY_POLICY = (
    "default-src 'none'; "
    "script-src 'self'; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data:; "
    "connect-src 'self'; "
    "frame-ancestors 'none'; "
    "base-uri 'self'; "
    "form-action 'self'"
)

# Segurança — endurecido apenas fora de DEBUG (produção exige HTTPS)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 365
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_REFERRER_POLICY = "same-origin"
    # Atrás de um reverse proxy que termina TLS, o proxy deve setar
    # X-Forwarded-Proto; ligar via env para o redirect HTTPS não entrar em loop.
    if env("USE_X_FORWARDED_PROTO"):
        SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    # A API é somente JSON em produção — desliga a Browsable API (HTML),
    # reduzindo superfície de XSS/escape de saída.
    REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = ("rest_framework.renderers.JSONRenderer",)
