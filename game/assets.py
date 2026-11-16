"""이미지 캐시 (한 번만 불러온다)."""
from pico2d import load_image
import config

_cache = {}


def image(name):
    if name not in _cache:
        _cache[name] = load_image(config.asset(name))
    return _cache[name]
