import os

env = os.getenv("DJANGO_SETTINGS_MODULE_ENV", "dev")

if env == "prod":
    from .prod import *
elif env == "hlm":
    from .hlm import *
else:
    from .dev import *