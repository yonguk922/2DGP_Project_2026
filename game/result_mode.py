"""결과 화면: 스테이지 클리어 / 게임 오버 / 최종 클리어."""
from pico2d import (clear_canvas, update_canvas, get_events,
                    SDL_QUIT, SDL_KEYDOWN, SDL_MOUSEBUTTONDOWN, SDLK_ESCAPE, SDLK_RETURN)

import assets
import config
import game_framework
import game_world
import save_data
import ui

kind = 'gameover'
stage = 1
remaining = 0
coins = 0
best = 0
new_record = False
LAST_STAGE = 3


def setup(k, stage_no, remain, earned):
    """저장 데이터를 갱신하고 표시할 값을 정해 둔다."""
    global kind, stage, remaining, coins, best, new_record
    kind, stage, remaining, coins = k, stage_no, remain, earned
    d = save_data.data
    d['coins'] += coins
    new_record = remain > d['best_soldiers']
    if new_record:
        d['best_soldiers'] = remain
    if k == 'clear':
        d['cleared_stage'] = max(d['cleared_stage'], stage_no)
    best = d['best_soldiers']
    save_data.save()


def init():
    pass


def finish():
    pass


def next_action():
    import play_mode
    import title_mode
    if kind == 'clear' and stage < LAST_STAGE:
        play_mode.stage_no = stage + 1
        game_framework.change_mode(play_mode)
    elif kind == 'clear':
        game_framework.change_mode(title_mode)
    else:
        play_mode.stage_no = stage
        game_framework.change_mode(play_mode)


def handle_events():
    import title_mode
    for e in get_events():
        if e.type == SDL_QUIT:
            game_framework.quit()
        elif e.type == SDL_KEYDOWN:
            if e.key == SDLK_RETURN:
                next_action()
            elif e.key == SDLK_ESCAPE:
                game_framework.change_mode(title_mode)
        elif e.type == SDL_MOUSEBUTTONDOWN:
            next_action()


def update():
    pass


def draw():
    W, H = config.W, config.H
    clear_canvas()
    game_world.render()                       # 마지막 장면을 배경으로 남겨 둔다
    ui.draw_img('px_black.png', W / 2, H / 2, W, H, alpha=0.65)
    if kind == 'clear':
        ui.draw_img('t_allclear.png' if stage >= LAST_STAGE else 't_clear.png', W / 2, 640)
    else:
        ui.draw_img('t_gameover.png', W / 2, 640)
    ui.draw_img('t_label_soldier.png', 170, 500)
    ui.text(str(remaining), 370, 500, 40, 'white', align='left')
    ui.draw_img('t_label_coin.png', 170, 440)
    ui.draw_img('coin.png', 330, 440)
    ui.text('+%d' % coins, 350, 440, 40, 'yellow', align='left')
    ui.draw_img('t_label_best.png', 170, 380)
    ui.text(str(best), 370, 380, 40, 'white', align='left')
    if kind == 'clear':
        ui.draw_img('t_next.png' if stage < LAST_STAGE else 't_totitle.png', W / 2, 240)
    else:
        ui.draw_img('t_retry.png', W / 2, 240)
    update_canvas()
