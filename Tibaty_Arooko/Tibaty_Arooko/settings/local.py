from .base import *

DEBUG = True

#TEMPLATE_DEBUG = DEBUG

EMAIL_HOST = "localhost"

EMAIL_PORT = 1025

DATABASES = { "default":
                  { "ENGINE": "django.db.backends.sqlite3",
                    "NAME": "temp.db",
                    "USER": "",
                    "PASSWORD": "",
                    "HOST": "",
                    "PORT": "",
                  }
}

INTERNAL_IPS = ("127.0.0.1",)

ALLOWED_HOSTS = ['arooko.ngrok.com', "127.0.0.1"]
