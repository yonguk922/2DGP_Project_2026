"""플레이 화면: 스테이지 데이터에 따라 게이트·적·보스를 생성하고 한 판을 진행한다."""
from pico2d import (clear_canvas, update_canvas, get_events,
                    SDL_QUIT, SDL_KEYDOWN, SDL_KEYUP, SDL_MOUSEMOTION, SDL_MOUSEBUTTONDOWN, SDL_MOUSEBUTTONUP,
                    SDLK_ESCAPE, SDLK_LEFT, SDLK_RIGHT, SDLK_a, SDLK_d)

import config
import fx
import game_framework
import game_world
import result_mode
import save_data
import stage_data
import title_mode
import ui
from boss import Boss
from bridge import Bridge
from enemy import KINDS
from gate import Gate
from hud import Hud
from squad import Squad

stage_no = 1
squad = None
boss = None
cfg = None
events = []
event_i = 0
keys = set()
dragging = False
paused = False
boss_spawned = False
boss_arrival_sent = False
boss_dead_sent = False

GATE_LEFT_X, GATE_RIGHT_X = 185, 355


def init():
    global squad, boss, cfg, events, event_i, keys, dragging, paused
    global boss_spawned, boss_arrival_sent, boss_dead_sent
    game_world.reset()
    cfg = stage_data.load(stage_no)
    events = sorted(cfg['events'], key=lambda e: e['at'])
    event_i = 0
    keys = set()
    dragging = False
    paused = False
    boss = None
    boss_spawned = boss_arrival_sent = boss_dead_sent = False

    game_world.add_object(Bridge(), 0)
    squad = Squad(save_data.start_soldiers())
    game_world.player = squad
    game_world.add_object(squad, 2)
    game_world.add_object(Hud(stage_no, cfg['boss_at']), 4)
    game_world.add_collision_pair('squad:enemy', squad, None)
    game_world.add_collision_pair('squad:ebullet', squad, None)
    game_world.scroll_speed = cfg['speed']


def finish():
    pass          # 마지막 장면은 결과 화면 배경으로 쓰기 위해 월드를 그대로 둔다


# ---------------------------------------------------------------- 입력
def handle_events():
    global paused, dragging
    for e in get_events():
        if e.type == SDL_QUIT:
            game_framework.quit()
        elif e.type == SDL_KEYDOWN:
            if e.key == SDLK_ESCAPE:
                paused = not paused
            elif e.key in (SDLK_LEFT, SDLK_a, SDLK_RIGHT, SDLK_d):
                keys.add(e.key)
        elif e.type == SDL_KEYUP:
            keys.discard(e.key)
        elif e.type == SDL_MOUSEBUTTONDOWN:
            dragging = True
            squad.target_x = e.x
        elif e.type == SDL_MOUSEMOTION and dragging:
            squad.target_x = e.x
        elif e.type == SDL_MOUSEBUTTONUP:
            dragging = False
            squad.target_x = None
    left = bool(keys & {SDLK_LEFT, SDLK_a})
    right = bool(keys & {SDLK_RIGHT, SDLK_d})
    squad.dir = int(right) - int(left)


# ---------------------------------------------------------------- 생성
def spawn_events():
    global event_i
    while event_i < len(events) and events[event_i]['at'] <= game_world.distance:
        spawn(events[event_i])
        event_i += 1


def add_enemy(e):
    game_world.add_object(e, 1)
    game_world.add_collision_pair('bullet:enemy', None, e)
    game_world.add_collision_pair('squad:enemy', None, e)


def spawn(ev):
    y = config.H + 60
    t = ev['type']
    if t == 'gates':
        gl = Gate(GATE_LEFT_X, y, ev['left']['op'], ev['left']['value'])
        gr = Gate(GATE_RIGHT_X, y, ev['right']['op'], ev['right']['value'])
        gl.partner, gr.partner = gr, gl
        for g in (gl, gr):
            game_world.add_object(g, 1)
            game_world.add_collision_pair('bullet:gate', None, g)
    elif t == 'grunts':
        count, cx = ev['count'], ev['x']
        per_row = 4
        for i in range(count):
            row, col = divmod(i, per_row)
            n_in_row = min(per_row, count - row * per_row)
            x = cx + (col - (n_in_row - 1) / 2) * 34
            add_enemy(KINDS['grunt'](x, y + row * 30))
    elif t in ('charger', 'shooter'):
        add_enemy(KINDS[t](ev['x'], y))


# ---------------------------------------------------------------- 갱신
def update():
    global boss, boss_spawned, boss_arrival_sent, boss_dead_sent
    if paused:
        return
    dt = game_framework.frame_time
    game_world.distance += game_world.scroll_speed * dt
    spawn_events()

    if not boss_spawned and game_world.distance >= cfg['boss_at']:
        boss_spawned = True
        boss = Boss(cfg['boss'])
        game_world.boss = boss
        game_world.add_object(boss, 3)
        game_world.add_collision_pair('bullet:boss', None, boss)
        fx.banner('t_boss.png', 560)

    game_world.update()
    game_world.handle_collisions()

    if boss and boss.arrived() and not boss_arrival_sent:
        boss_arrival_sent = True
        game_world.scroll_speed = 0.0                      # 보스전: 스크롤 정지
        squad.sm.add_event(('BOSS_ARRIVED', 0))
    if boss and boss.is_dying() and not boss_dead_sent:
        boss_dead_sent = True
        squad.sm.add_event(('BOSS_DEAD', 0))

    if squad.dead_finished():
        coins = game_world.stats['coins']
        result_mode.setup('gameover', stage_no, 0, coins)
        game_framework.change_mode(result_mode)
    elif squad.win_finished():
        coins = game_world.stats['coins'] + squad.n + 50 * stage_no
        result_mode.setup('clear', stage_no, squad.n, coins)
        game_framework.change_mode(result_mode)


def draw():
    clear_canvas()
    game_world.render()
    if paused:
        ui.draw_img('px_black.png', config.W / 2, config.H / 2, config.W, config.H, alpha=0.6)
        ui.draw_img('t_pause.png', config.W / 2, config.H / 2)
    update_canvas()
