"""JSON 저장 / 불러오기: 코인, 업그레이드 레벨, 최고 기록."""
import json
import os

import config

PATH = os.path.join(config.BASE, 'save.json')
DEFAULT = {'coins': 0, 'start_level': 0, 'best_soldiers': 0, 'cleared_stage': 0}
MAX_LEVEL = 5
START_SOLDIERS = 10
PER_LEVEL = 5

data = dict(DEFAULT)


def load():
    global data
    data = dict(DEFAULT)
    try:
        with open(PATH, 'r', encoding='utf-8') as f:
            data.update(json.load(f))
    except (OSError, ValueError):
        pass
    return data


def save():
    try:
        with open(PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def start_soldiers():
    return START_SOLDIERS + PER_LEVEL * data['start_level']


def upgrade_cost():
    return 100 * (data['start_level'] + 1)


def try_upgrade():
    if data['start_level'] >= MAX_LEVEL or data['coins'] < upgrade_cost():
        return False
    data['coins'] -= upgrade_cost()
    data['start_level'] += 1
    save()
    return True
