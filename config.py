import json

DEFAULT_FILE_PATH = "default_config.json"

def get_config(file_path: str = DEFAULT_FILE_PATH):
    with open(file_path) as f:
        config = json.loads(f.read())
    return config