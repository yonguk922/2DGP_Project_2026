"""헤드리스(창 없이) 자동 플레이 테스트 + 스크린샷.
   python tests/headless_test.py [스테이지번호 ...]      결과 이미지는 /tmp/shots 에 저장
봇이 게이트를 고르고 보스 경고를 피하며 클리어가 가능한지 확인한다."""
import ctypes
import os
import sys

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_RENDER_DRIVER', 'software')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

import sdl2
from PIL import Image
from pico2d import open_canvas
import pico2d.pico2d as p2

import config
open_canvas(config.W, config.H)

import game_framework, game_world, play_mode, result_mode, save_data, title_mode
from squad import Run, Fight

save_data.PATH = '/tmp/test_save.json'
OUT = '/tmp/shots'
os.makedirs(OUT, exist_ok=True)


def shot(name):
    W, H = config.W, config.H
    buf = ctypes.create_string_buffer(W * H * 4)
    sdl2.SDL_RenderReadPixels(p2.renderer, None, sdl2.SDL_PIXELFORMAT_ABGR8888, buf, W * 4)
    Image.frombuffer('RGBA', (W, H), buf, 'raw', 'RGBA', 0, 1).convert('RGB').save('%s/%s.png' % (OUT, name))


import random
NOISE = float(os.environ.get('BOT_NOISE', '0'))
_hold = [0, 0]


def bot(sq):
    if NOISE:
        if _hold[0] > 0:
            _hold[0] -= 1
            sq.dir = _hold[1]
            return
        _hold[0] = random.randint(8, 20)
    _bot(sq)
    if NOISE:
        _hold[1] = sq.dir if random.random() > NOISE else random.choice([-1, 0, 1])
        sq.dir = _hold[1]


def _bot(sq):
    """간단한 규칙 기반 봇: 보스 경고 회피 → 게이트 선택 → 적 쪽으로 정렬."""
    boss = game_world.boss
    target = None
    if boss and boss.arrived() and boss.sm.cur_state.__name__ in ('Warn', 'Attack') and boss.pattern == 'slam':
        # 경고 구역에서 최대한 멀리
        lo, hi = config.BRIDGE_L + 70, config.BRIDGE_R - 70
        target = hi if boss.warn_x < config.W / 2 else lo
    if target is None:
        gates = [g for g in game_world.layers[1] if g.__class__.__name__ == 'Gate' and not g.used and g.y > sq.y - 50]
        gates.sort(key=lambda g: g.y)
        if gates and gates[0].y < 720:
            pair = [g for g in gates if abs(g.y - gates[0].y) < 5]
            best = max(pair, key=lambda g: g.apply(sq.n) + (6 if g.op == 'div' else 0))
            target = best.x
    if target is None:
        en = [e for e in game_world.layers[1] if e.__class__.__name__ in ('Grunt', 'Charger', 'Shooter') and e.y > sq.y]
        if en:
            en.sort(key=lambda e: e.y)
            target = en[0].x
        elif boss:
            target = boss.x
    if target is None:
        sq.dir = 0
    else:
        dx = target - sq.x
        sq.dir = 0 if abs(dx) < 8 else (1 if dx > 0 else -1)


def run_stage(n, shots=True, max_sec=180):
    play_mode.stage_no = n
    game_framework.stack[:] = [play_mode]
    play_mode.init()
    game_framework.frame_time = 1 / 60
    t, taken = 0.0, set()
    sq = play_mode.squad
    log = []
    while game_framework.stack[-1] is play_mode and t < max_sec:
        bot(play_mode.squad)
        play_mode.update()
        t += 1 / 60
        gw = game_world
        if shots:
            tag = None
            if int(t * 60) == 120:
                tag = 's%d_start' % n
            b = gw.boss
            gl = [g for g in gw.layers[1] if g.__class__.__name__ == 'Gate' and not g.used]
            en = [e for e in gw.layers[1] if e.__class__.__name__ != 'Gate' and 350 < e.y < 800]
            if gl and 430 < gl[0].y < 520 and 's%d_gate' % n not in taken:
                tag = 's%d_gate' % n
            if len(en) >= 5 and 400 < en[0].y < 700 and 's%d_enemy' % n not in taken and int(t) > 6:
                tag = 's%d_enemy' % n
            if b and b.arrived() and 't%d' % n not in taken and b.hp < b.max_hp * 0.6 and b.sm.cur_state.__name__ == 'Idle':
                taken.add('t%d' % n)
                tag = 's%d_boss_fight' % n
            if b and b.arrived() and 'boss' not in taken and b.sm.cur_state.__name__ == 'Warn' and b.pattern == 'slam':
                tag, _ = 's%d_boss_warn' % n, taken.add('boss')
            if tag and tag not in taken:
                taken.add(tag)
                play_mode.draw()
                shot(tag)
        if int(t * 60) % 300 == 0:
            log.append((round(t), play_mode.squad.n, round(gw.distance)))
    play_mode.draw()
    return t, log


if __name__ == '__main__':
    stages = [int(a) for a in sys.argv[1:]] or [1, 2, 3]
    for n in stages:
        save_data.data = dict(save_data.DEFAULT)
        t, log = run_stage(n)
        mode = game_framework.stack[-1]
        res = (result_mode.kind, result_mode.remaining, result_mode.coins) if mode is result_mode else ('timeout', play_mode.squad.n, 0)
        print('stage', n, 'time %.1fs' % t, 'result', res)
        print('   squad/dist log:', log)
        if mode is result_mode:
            result_mode.draw()
            shot('s%d_result' % n)
