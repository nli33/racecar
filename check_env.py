from config import get_config
from env import RacecarEnv
from gymnasium.utils.env_checker import check_env

check_env(RacecarEnv(get_config()))