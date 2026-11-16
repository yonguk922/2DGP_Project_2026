"""스테이지 데이터(data/stage_N.json) 생성기.  게이트·적 배치를 여기서 설계한다.
at = 다리를 달린 누적 거리(px).  수치는 플레이 테스트하며 조정한다."""
import json
import os

OUT = os.path.join(os.path.dirname(__file__), '..', 'data')


def add(v):
    return {'op': 'add', 'value': v}


def mul(v):
    return {'op': 'mul', 'value': v}


def div(v):
    return {'op': 'div', 'value': v}


def gates(at, l, r):
    return {'at': at, 'type': 'gates', 'left': l, 'right': r}


def grunts(at, x, count):
    return {'at': at, 'type': 'grunts', 'x': x, 'count': count}


def charger(at, x):
    return {'at': at, 'type': 'charger', 'x': x}


def shooter(at, side):
    return {'at': at, 'type': 'shooter', 'x': 110 if side == 'L' else 430}


STAGES = {
    1: {  # 튜토리얼 · 쉬운 선택 (+, × 위주, 일반 무리, 중간 보스 패턴 1개)
        'name': 'Stage 1', 'speed': 200, 'boss_at': 5600,
        'events': [
            gates(500, add(10), add(-8)),
            grunts(1300, 270, 6),
            gates(2000, mul(2), add(5)),
            grunts(2700, 190, 4), grunts(2700, 350, 4),
            gates(3400, add(15), div(2)),
            grunts(4100, 270, 8),
            gates(4700, add(12), add(-10)),
        ],
        'boss': {'hp': 400, 'patterns': ['slam'], 'cooldown': 1.6, 'slam_base': 8, 'slam_ratio': 0.10},
    },
    2: {  # 위험한 게이트 등장, 돌진형 추가, 강화된 중간 보스
        'name': 'Stage 2', 'speed': 220, 'boss_at': 7000,
        'events': [
            gates(500, add(-12), add(8)),
            grunts(1200, 270, 8),
            charger(1700, 200),
            gates(2300, div(2), add(10)),
            grunts(3000, 190, 5), grunts(3000, 350, 5), charger(3300, 350),
            gates(3900, add(-20), mul(2)),
            charger(4500, 180), charger(4650, 360), grunts(4900, 270, 6),
            gates(5500, add(-15), div(2)),
            grunts(6100, 270, 8),
        ],
        'boss': {'hp': 550, 'patterns': ['slam'], 'cooldown': 1.0, 'slam_base': 10, 'slam_ratio': 0.14},
    },
    3: {  # 모든 요소 총동원: 연속 게이트, 쏴서 뒤집기, 원거리형, 최종 보스(패턴 3개)
        'name': 'Stage 3', 'speed': 240, 'boss_at': 8800,
        'events': [
            gates(500, add(-10), add(10)),
            gates(900, add(8), add(-15)),
            shooter(1300, 'L'), shooter(1500, 'R'), grunts(1700, 270, 8),
            gates(2400, div(2), add(-20)),
            charger(3000, 270), grunts(3200, 190, 6), grunts(3200, 350, 6),
            gates(3900, add(-18), mul(2)),
            shooter(4400, 'L'), shooter(4400, 'R'), charger(4800, 270),
            gates(5400, div(2), div(2)),
            gates(5800, add(-10), mul(2)),
            grunts(6300, 270, 12), charger(6600, 200), charger(6700, 340),
            gates(7300, add(12), add(-25)),
            shooter(7800, 'L'), grunts(7900, 300, 6),
        ],
        'boss': {'hp': 1400, 'patterns': ['slam', 'fan', 'summon'], 'cooldown': 1.0,
                 'slam_base': 10, 'slam_ratio': 0.16, 'fan_count': 9},
    },
}

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for n, cfg in STAGES.items():
        with open(os.path.join(OUT, 'stage_%d.json' % n), 'w', encoding='utf-8') as f:
            json.dump(cfg, f, ensure_ascii=False, indent=1)
    print('stages written')
