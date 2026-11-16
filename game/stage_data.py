"""스테이지 데이터(JSON) 불러오기. 게이트·적 배치는 코드가 아니라 data/stage_N.json 에 있다."""
import json

import config


def load(stage_no):
    with open(config.data_path('stage_%d.json' % stage_no), 'r', encoding='utf-8') as f:
        return json.load(f)
