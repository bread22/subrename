import json
import os


def load_config():
    abs_path = os.path.abspath(__file__)
    dir_name = os.path.dirname(abs_path)
    with open(os.path.join(dir_name, 'config.json')) as fn:
        config = fn.read()
    return json.loads(config)
