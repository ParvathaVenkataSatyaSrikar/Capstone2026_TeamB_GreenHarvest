"""Theme bootstrap — loads env and applies semantic colors from brand.py."""
from config.settings import _load_env_file, get_settings


def bootstrap_app():
    _load_env_file()
    get_settings()
