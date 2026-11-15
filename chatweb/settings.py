import os
from pathlib import Path

from django.core.management.utils import get_random_secret_key

BASE_DIR = Path(__file__).resolve().parent.parent

# Configuración por variables de entorno (ver .env.example). Ninguna clave va en el repo.
# Si no se define DJANGO_SECRET_KEY se genera una aleatoria en cada arranque.
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY") or get_random_secret_key()
DEBUG = os.getenv("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "*"]

CSRF_TRUSTED_ORIGINS = ["https://*.trycloudflare.com"]

INSTALLED_APPS = [
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "chat",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
]
ROOT_URLCONF = "chatweb.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": ["django.template.context_processors.request"]},
}]
WSGI_APPLICATION = "chatweb.wsgi.application"
# Sin base de datos: la sesión vive en una cookie firmada, no hace falta migrate
DATABASES = {}
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
LANGUAGE_CODE = "es-cl"
TIME_ZONE = "America/Santiago"
USE_TZ = True
STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Carpeta donde viven los bots (.py) que aparecen en la barra izquierda
BOTS_DIR = BASE_DIR / "bots"
