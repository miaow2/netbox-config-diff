import os

ALLOWED_HOSTS = ["*"]

DATABASE = {
    "NAME": os.environ.get("POSTGRES_DB", "netbox"),
    "USER": os.environ.get("POSTGRES_USER", "netbox"),
    "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "netbox"),
    "HOST": os.environ.get("POSTGRES_HOST", "postgres"),
    "PORT": 5432,
}

SECRET_KEY = os.environ.get("SECRET_KEY", "dummydummydummydummydummydummydummydummydummydummy")

REDIS = {
    "tasks": {
        "HOST": os.environ.get("REDIS_HOST", "redis"),
        "PORT": 6379,
        "PASSWORD": os.environ.get("REDIS_PASSWORD", "redis"),
        "DATABASE": 0,
        "SSL": False,
    },
    "caching": {
        "HOST": os.environ.get("REDIS_HOST", "redis"),
        "PORT": 6379,
        "PASSWORD": os.environ.get("REDIS_PASSWORD", "redis"),
        "DATABASE": 1,
        "SSL": False,
    },
}

DEBUG = True
DEVELOPER = True

INTERNAL_IPS = ("0.0.0.0", "127.0.0.1", "::1")

PLUGINS = [
    "netbox_config_diff",
]
PLUGINS_CONFIG = {
    "netbox_config_diff": {
        "USERNAME": "foo",
        "PASSWORD": "bar",
    }
}

SCRIPTS_ROOT = "scripts"
