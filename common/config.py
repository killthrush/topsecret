import os
from collections import namedtuple

DEFAULT_CONFIG = "dev"


def _create_config(env):
    config = {
        "dev": {
            "app_name": "topsecret",
            "mongo_uri": "mongodb://localhost:27017",
            "email_collection": "email",
            "source_collection": "source"
        },
        "build_buddy": {
            "app_name": "topsecret",
            "mongo_uri": "mongodb://mongo:27017",
            "email_collection": "email",
            "source_collection": "source"
        }
    }
    config_type = namedtuple('Config', config[env].keys())
    return config_type(**config[env])


current_config = os.getenv('ENVIRONMENT_CONFIG_KEY', DEFAULT_CONFIG)
AppConfig = _create_config(current_config)
