import os
import logging.config
from dotenv import load_dotenv


load_dotenv()

dsn = os.getenv("SENTRY_DSN")
LOGLEVEL = os.getenv("LOG_LEVEL")


logging.config.dictConfig({
    "version": 1,
    "disable_existing_logger": False,
    "formatters": {
        "console": {
            "format": "%(asctime)s %(levelname)s [%(name)s:%(lineno)s] %(module)s %(message)s"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "console",
        },
    },
    "loggers": {
        "": {
            "level": LOGLEVEL,
            "handlers": [
                "console",
            ]
        }
    }
})

