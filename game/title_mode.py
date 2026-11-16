"""타이틀 화면."""
from pico2d import (clear_canvas, update_canvas, get_events,
                    SDL_QUIT, SDL_KEYDOWN, SDL_MOUSEBUTTONDOWN,
                    SDLK_ESCAPE, SDLK_RETURN, SDLK_r, SDLK_u, SDLK_1, SDLK_2, SDLK_3)

import assets
import config
import game_framework
import game_world
import save_data
import ui

t = 0.0
RESET_RECT = (150, 70, 390, 108)


def init():
    global t
    t = 0.0
    save_data.load()
    game_world.reset()


def finish():
    pass


def start_stage(n):
    import play_mode
    play_mode.stage_no = n
    game_framework.change_mode(play_mode)


def reset_progress():
    save_data.reset()


def handle_events():
    for e in get_events():
        if e.type == SDL_QUIT:
            game_framework.quit()
        elif e.type == SDL_KEYDOWN:
            if e.key == SDLK_ESCAPE:
                game_framework.quit()
            elif e.key == SDLK_r:
                reset_progress()
            elif e.key == SDLK_RETURN:
                start_stage(1)
            elif e.key in (SDLK_1, SDLK_2, SDLK_3):
                n = {SDLK_1: 1, SDLK_2: 2, SDLK_3: 3}[e.key]
                if n <= save_data.data['cleared_stage'] + 1 or True:     # 데모/테스트를 위해 모든 스테이지 선택 허용
                    start_stage(n)
            elif e.key == SDLK_u:
                save_data.try_upgrade()
        elif e.type == SDL_MOUSEBUTTONDOWN:
            if RESET_RECT[0] <= e.x <= RESET_RECT[2] and RESET_RECT[1] <= e.y <= RESET_RECT[3]:
                reset_progress()
                return
            start_stage(1)


def update():
    global t
    t += game_framework.frame_time
    game_world.distance += 70 * game_framework.frame_time


def draw():
    import math
    W, H = config.W, config.H
    clear_canvas()
    off = game_world.distance % H
    bg = assets.image('bridge.png')
    bg.draw(W / 2, H / 2 - off)
    bg.draw(W / 2, H / 2 - off + H)
    ui.draw_img('px_black.png', W / 2, H / 2, W, H, alpha=0.6)

    ui.draw_img('t_title.png', W / 2, 700)
    ui.draw_img('t_sub.png', W / 2, 600)

    # 달리는 병사 장식
    sold = assets.image('soldier.png')
    f = int(t * 9) % 4
    from squad import OFFSETS
    for ox, oy in OFFSETS[:24]:
        sold.clip_draw(f * 40, 0, 40, 40, W / 2 + ox * 1.3, 430 + oy * 1.3, 34, 34)

    a = 0.55 + 0.45 * (0.5 + 0.5 * math.sin(t * 4))
    ui.draw_img('t_start.png', W / 2, 312, alpha=a)
    ui.draw_img('t_select.png', W / 2, 268)

    # 업그레이드 안내
    d = save_data.data
    ui.draw_img('t_label_coins_have.png', 110, 214)
    ui.draw_img('coin.png', 178, 214)
    ui.text(str(d['coins']), 196, 214, 26, 'yellow', align='left')
    ui.draw_img('t_label_start.png', 350, 214)
    ui.text(str(save_data.start_soldiers()), 408, 214, 26, 'white', align='left')
    ui.draw_img('t_upgrade.png', W / 2, 166)
    if d['start_level'] >= save_data.MAX_LEVEL:
        ui.draw_img('t_maxlv.png', W / 2, 126)
    else:
        ui.draw_img('t_label_cost.png', 210, 126)
        ui.draw_img('coin.png', 262, 126)
        ui.text(str(save_data.upgrade_cost()), 282, 126, 24, 'yellow', align='left')
    ui.draw_img('t_help.png', W / 2, 52)
    ui.draw_img('t_reset.png', W / 2, 90)
    update_canvas()
