import json

DEFAULT_FILE_PATH = "config.json"

def get_config(file_path: str = DEFAULT_FILE_PATH) -> dict:
    with open(file_path) as f:
        config = json.loads(f.read())
    return config

def write_config(config: dict, file_path: str = DEFAULT_FILE_PATH) -> bool:
    if config is None or config == {}:
        return False
    with open(file_path, "w") as f:
        f.write(json.dumps(config))
    return True