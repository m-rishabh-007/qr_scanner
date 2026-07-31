from datetime import timedelta
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parents[2]
env = environ.Env()
env_file = BASE_DIR.parent / ".env"
if env_file.exists():
    environ.Env.read_env(env_file)

PRODUCT_NAME = env("PRODUCT_NAME", default="ReviewFlow")
COMPANY_NAME = env("COMPANY_NAME", default="Example Company")
PUBLIC_BASE_URL = env("PUBLIC_BASE_URL", default="http://localhost:8000").rstrip("/")
SUPPORT_EMAIL = env("SUPPORT_EMAIL", default="support@example.test")
PRIVACY_EMAIL = env("PRIVACY_EMAIL", default="privacy@example.test")

SECRET_KEY = env("DJANGO_SECRET_KEY", default="unsafe-local-secret")
DEBUG = env.bool("DJANGO_DEBUG", default=False)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    "apps.core",
    "apps.accounts",
    "apps.catalog",
    "apps.locations",
    "apps.feedback",
    "apps.generation",
    "apps.analytics",
    "apps.public_site",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.product_identity",
            ]
        },
    }
]

DATABASES = {"default": env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": env("PUBLIC_THROTTLE_ANON", default="60/minute"),
        "user": "300/minute",
        "generation": env("GENERATION_THROTTLE_ANON", default="10/minute"),
    },
    "PAGE_SIZE": 25,
}

SPECTACULAR_SETTINGS = {
    "TITLE": f"{PRODUCT_NAME} API",
    "VERSION": "0.1.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=env.int("ACCESS_TOKEN_MINUTES", default=10)),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=env.int("REFRESH_TOKEN_DAYS", default=14)),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
}

EMAIL_BACKEND = env(
    "EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = env("EMAIL_HOST", default="")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_TIMEOUT = 10
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default=f"{PRODUCT_NAME} <noreply@example.test>")

EMAIL_VERIFICATION_HOURS = env.int("EMAIL_VERIFICATION_HOURS", default=24)
PASSWORD_RESET_HOURS = env.int("PASSWORD_RESET_HOURS", default=2)
PASSWORD_RESET_TIMEOUT = PASSWORD_RESET_HOURS * 3600
MERCHANT_APPROVAL_REQUIRED = env.bool("MERCHANT_APPROVAL_REQUIRED", default=True)

GOOGLE_REVIEW_ALLOWED_HOSTS = set(
    env.list(
        "GOOGLE_REVIEW_ALLOWED_HOSTS",
        default=["g.page", "search.google.com", "www.google.com", "maps.google.com", "maps.app.goo.gl", "goo.gl"],
    )
)
GOOGLE_REVIEW_LINK_TIMEOUT_SECONDS = env.int("GOOGLE_REVIEW_LINK_TIMEOUT_SECONDS", default=8)

LITELLM_BASE_URL = env("LITELLM_BASE_URL", default="http://litellm:4000/v1").rstrip("/")
LITELLM_API_KEY = env("LITELLM_API_KEY", default="")
LITELLM_MODEL = env("LITELLM_MODEL", default="review-assistant")
LITELLM_TIMEOUT_SECONDS = env.int("LITELLM_TIMEOUT_SECONDS", default=20)
LITELLM_MAX_CONCURRENCY = env.int("LITELLM_MAX_CONCURRENCY", default=4)
LITELLM_TEMPERATURE = env.float("LITELLM_TEMPERATURE", default=0.25)
MAX_GENERATIONS_PER_SESSION = env.int("MAX_GENERATIONS_PER_SESSION", default=2)
MAX_COMMENT_LENGTH = env.int("MAX_COMMENT_LENGTH", default=1200)
MAX_REVIEW_LENGTH = env.int("MAX_REVIEW_LENGTH", default=1500)

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "same-origin"
