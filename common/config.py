from collections import namedtuple


def _create_config():
    config = {
        "app_name": "topsecret",
        "mongo_uri": "mongodb://localhost:27017",
        "email_collection": "email",
        "source_collection": "source"
    }
    config_type = namedtuple('Config', config.keys())
    return config_type(**config)

AppConfig = _create_config()

