"""병사 무리 (Squad): 수·대형·이동·자동 사격 + 상태 머신(RUN / FIGHT / WIN / DEAD)."""
import math
import random

import assets
import config
import fx
import game_framework
import game_world
import ui
from bullet import Bullet
from state_machine import StateMachine, event_is

SHOW_MAX = 100          # 화면에는 최대 100명까지만 그린다
SPACING = 11.0          # 병사 간격 (해바라기 나선 배치)
FIRE_INTERVAL = 0.30
MAX_SHOTS = 12
MOVE_SPEED = 430.0
DRAG_SPEED = 1000.0

# 나선(황금각) 배치 좌표를 미리 계산 → 병사 수가 늘면 원이 커진다
OFFSETS = []
for _i in range(SHOW_MAX):
    _r = SPACING * math.sqrt(_i + 0.5)
    _a = _i * 2.399963
    OFFSETS.append((_r * math.cos(_a), _r * math.sin(_a) * 0.9))


# ---------------------------------------------------------------- 상태
class Run:
    @staticmethod
    def enter(sq, e):
        sq.anim_fps = 9

    @staticmethod
    def exit(sq, e):
        pass

    @staticmethod
    def do(sq):
        sq.animate()
        sq.fire()

    @staticmethod
    def draw(sq):
        sq.draw_soldiers()


class Fight:
    """보스전: 다리 스크롤은 멈추고 제자리에서 사격."""

    @staticmethod
    def enter(sq, e):
        sq.anim_fps = 5

    @staticmethod
    def exit(sq, e):
        pass

    @staticmethod
    def do(sq):
        sq.animate()
        sq.fire()

    @staticmethod
    def draw(sq):
        sq.draw_soldiers()


class Win:
    @staticmethod
    def enter(sq, e):
        sq.anim_fps = 12
        sq.state_t = 0.0

    @staticmethod
    def exit(sq, e):
        pass

    @staticmethod
    def do(sq):
        sq.animate()
        sq.state_t += game_framework.frame_time

    @staticmethod
    def draw(sq):
        sq.draw_soldiers(bounce=True)


class Dead:
    """소멸 연출: 병사들이 사방으로 흩어지며 사라진다."""
    DURATION = 0.9

    @staticmethod
    def enter(sq, e):
        sq.state_t = 0.0
        fx.pop(sq.x, sq.y, 'red', 200)

    @staticmethod
    def exit(sq, e):
        pass

    @staticmethod
    def do(sq):
        sq.state_t += game_framework.frame_time
        sq.frame += 12 * game_framework.frame_time

    @staticmethod
    def draw(sq):
        t = min(1.0, sq.state_t / Dead.DURATION)
        img = sq.image
        img.opacify(1 - t)
        for ox, oy in sq.ghost:
            k = 1 + 2.2 * t
            img.clip_draw(int(sq.frame) % 4 * 40, 0, 40, 40, sq.x + ox * k, sq.y + oy * k, 28, 28)
        img.opacify(1.0)


class Squad:
    def __init__(self, n):
        self.n = n
        self.x = config.W / 2
        self.y = config.SQUAD_Y
        self.dir = 0                 # 키보드 이동 방향 (-1, 0, 1)
        self.target_x = None         # 마우스 드래그 목표
        self.frame = 0.0
        self.anim_fps = 9
        self.fire_t = 0.0
        self.state_t = 0.0
        self.hurt_t = 0.0
        self.ghost = []
        self.image = assets.image('soldier.png')
        self.pill = assets.image('pill.png')
        self.sm = StateMachine(self)
        self.sm.start(Run)
        self.sm.set_transitions({
            Run: {event_is('BOSS_ARRIVED'): Fight, event_is('ALL_DEAD'): Dead},
            Fight: {event_is('BOSS_DEAD'): Win, event_is('ALL_DEAD'): Dead},
            Win: {},
            Dead: {},
        })

    # ---- 크기 / 판정
    def shown(self):
        return min(self.n, SHOW_MAX)

    def radius(self):
        return SPACING * math.sqrt(max(1, self.shown())) + 12

    def get_bb(self):
        r = self.radius() * 0.85
        return self.x - r, self.y - r, self.x + r, self.y + r

    def alive_for_gate(self):
        return self.sm.cur_state in (Run, Fight) and self.n > 0

    def is_dead(self):
        return self.sm.cur_state is Dead

    def dead_finished(self):
        return self.sm.cur_state is Dead and self.state_t >= Dead.DURATION

    def win_finished(self):
        return self.sm.cur_state is Win and self.state_t >= 1.6

    # ---- 피해 / 사망
    def take(self, k):
        if self.sm.cur_state not in (Run, Fight) or k <= 0:
            return
        k = min(k, self.n)
        fx.pop(self.x, self.y + self.radius() * 0.5, 'blue', 70)
        fx.float_text(self.x + random.randint(-30, 30), self.y + self.radius() + 20, '−%d' % k, 'red', 30)
        self.n -= k
        self.hurt_t = 0.15
        if self.n <= 0:
            self.kill()

    def kill(self):
        self.n = 0
        if self.sm.cur_state in (Run, Fight):
            self.ghost = list(OFFSETS[:max(6, min(SHOW_MAX, 20))])
            self.sm.handle_event(('ALL_DEAD', 0))      # 즉시 전이 (같은 프레임에 게임오버 연출 시작)

    # ---- 갱신
    def update(self):
        dt = game_framework.frame_time
        self.hurt_t = max(0.0, self.hurt_t - dt)
        if self.sm.cur_state in (Run, Fight):
            self.move(dt)
        self.sm.update()

    def move(self, dt):
        if self.target_x is not None:                      # 마우스 드래그
            dx = self.target_x - self.x
            self.x += max(-DRAG_SPEED * dt, min(DRAG_SPEED * dt, dx))
        else:
            self.x += self.dir * MOVE_SPEED * dt
        # 다리 밖으로는 못 나감
        r = min(self.radius(), 120)
        self.x = max(config.BRIDGE_L + r * 0.75, min(config.BRIDGE_R - r * 0.75, self.x))

    def animate(self):
        self.frame += self.anim_fps * game_framework.frame_time

    def fire(self):
        """병사 수에 비례해 앞쪽으로 총알 발사 (발사 수 상한 있음)."""
        self.fire_t -= game_framework.frame_time
        if self.fire_t > 0 or self.n <= 0:
            return
        self.fire_t = FIRE_INTERVAL / self.fire_rate
        shots = min(1 + self.n // 8, MAX_SHOTS)
        pts = random.sample(OFFSETS[:self.shown()], min(shots, self.shown()))
        for ox, oy in pts:
            b = Bullet(self.x + ox, self.y + oy + 14, self.bullet_damage)
            game_world.add_object(b, 2)
            game_world.add_collision_pair('bullet:enemy', b, None)
            game_world.add_collision_pair('bullet:gate', b, None)
            game_world.add_collision_pair('bullet:boss', b, None)

    fire_rate = 1.0
    bullet_damage = 1

    # ---- 그리기
    def draw_soldiers(self, bounce=False):
        f = int(self.frame) % 4
        flash = self.hurt_t > 0
        if flash:
            self.image.opacify(0.55)
        for i in range(self.shown()):
            ox, oy = OFFSETS[i]
            if bounce:
                oy += 6 * math.sin(self.frame * 1.2 + i)
            self.image.clip_draw(f * 40, 0, 40, 40, self.x + ox, self.y + oy, 28, 28)
        if flash:
            self.image.opacify(1.0)

    def draw(self):
        self.sm.draw()
        if self.sm.cur_state is not Dead:
            ly = max(24, self.y - self.radius() - 14)
            self.pill.draw(self.x, ly, 96, 34)
            ui.text(str(self.n), self.x, ly, 26, 'white')

    def handle_collision(self, group, other):
        if group == 'squad:ebullet':
            self.take(other.damage)
