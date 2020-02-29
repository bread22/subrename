import json


def load_config():
    with open('config.json') as fn:
        config = fn.read()
    return json.loads(config)
