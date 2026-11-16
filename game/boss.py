"""보스: HP 바 + 패턴 상태 머신 (ENTER → IDLE → WARN → ATTACK → COOLDOWN → … → DEAD)."""
import math
import random

import assets
import config
import fx
import game_framework
import game_world
import ui
from bullet import spawn_enemy_bullet
from enemy import Grunt
from state_machine import StateMachine, event_is

STOP_Y = 690            # 보스가 멈춰 서는 화면 y


class Enter:
    @staticmethod
    def enter(b, e):
        pass

    @staticmethod
    def exit(b, e):
        pass

    @staticmethod
    def do(b):
        b.y -= game_world.scroll_speed * game_framework.frame_time
        if b.y <= STOP_Y:
            b.y = STOP_Y
            b.sm.add_event(('ARRIVED', 0))

    @staticmethod
    def draw(b):
        b.draw_body()


class Idle:
    @staticmethod
    def enter(b, e):
        b.t = 0.0

    @staticmethod
    def exit(b, e):
        pass

    @staticmethod
    def do(b):
        b.t += game_framework.frame_time
        b.bob()
        if b.t >= 0.6 / b.speed_scale:
            b.sm.add_event(('TIMEOUT', 0))

    @staticmethod
    def draw(b):
        b.draw_body()


class Warn:
    """공격 전 경고: 어떤 패턴인지 바닥/보스 표시로 알려 준다."""
    DURATION = 1.1

    @staticmethod
    def enter(b, e):
        b.t = 0.0
        b.pattern = b.patterns[b.pattern_i % len(b.patterns)]
        b.pattern_i += 1
        if b.pattern == 'slam':
            sq = game_world.player
            b.warn_x = sq.x if sq else config.W / 2          # 경고 위치 고정 → 피할 수 있다

    @staticmethod
    def exit(b, e):
        pass

    @staticmethod
    def do(b):
        b.t += game_framework.frame_time
        b.bob()
        if b.t >= Warn.DURATION / b.speed_scale:
            b.sm.add_event(('TIMEOUT', 0))

    @staticmethod
    def draw(b):
        blink = 0.25 + 0.2 * math.sin(b.t * 22)
        if b.pattern == 'slam':
            top = b.y - 90
            ui.draw_img('warning.png', b.warn_x, top / 2, b.SLAM_W, top, alpha=blink)
        b.draw_body()
        if b.pattern != 'slam':                              # 부채꼴/소환은 보스가 붉게 깜빡
            ui.draw_img('fx_pop_red.png', b.x, b.y, 230 + 20 * math.sin(b.t * 18), 230, alpha=blink + 0.3)


class Attack:
    @staticmethod
    def enter(b, e):
        b.t = 0.0
        b.volley = 0
        b.mouth = 0.35
        if b.pattern == 'slam':
            b.do_slam()
        elif b.pattern == 'summon':
            b.do_summon()

    @staticmethod
    def exit(b, e):
        pass

    @staticmethod
    def do(b):
        dt = game_framework.frame_time
        b.t += dt
        b.mouth = max(b.mouth, 0.2)
        if b.pattern == 'fan' and b.volley < 3 and b.t >= b.volley * 0.4 / b.speed_scale:
            b.do_fan()
            b.volley += 1
        limit = {'slam': 0.4, 'fan': 1.3, 'summon': 0.6}[b.pattern] / b.speed_scale
        if b.t >= limit:
            b.sm.add_event(('TIMEOUT', 0))

    @staticmethod
    def draw(b):
        b.draw_body()


class Cooldown:
    @staticmethod
    def enter(b, e):
        b.t = 0.0

    @staticmethod
    def exit(b, e):
        pass

    @staticmethod
    def do(b):
        b.t += game_framework.frame_time
        b.bob()
        if b.t >= b.cooldown / b.speed_scale:
            b.sm.add_event(('TIMEOUT', 0))

    @staticmethod
    def draw(b):
        b.draw_body()


class Dead:
    DURATION = 1.4

    @staticmethod
    def enter(b, e):
        b.t = 0.0
        fx.flash(0.7)

    @staticmethod
    def exit(b, e):
        pass

    @staticmethod
    def do(b):
        b.t += game_framework.frame_time
        if int(b.t * 14) != int((b.t - game_framework.frame_time) * 14):
            fx.pop(b.x + random.randint(-80, 80), b.y + random.randint(-80, 80), random.choice(['red', 'white']), 90)
        if b.t >= Dead.DURATION:
            game_world.remove_object(b)

    @staticmethod
    def draw(b):
        b.draw_body(alpha=max(0.0, 1 - b.t / Dead.DURATION))


class Boss:
    SIZE = 200
    SLAM_W = 150

    def __init__(self, cfg):
        self.x = config.W / 2
        self.y = config.H + 160
        self.max_hp = cfg['hp']
        self.hp = self.max_hp
        self.patterns = cfg['patterns']
        self.cooldown = cfg.get('cooldown', 1.5)
        self.slam_base = cfg.get('slam_base', 8)           # 내려찍기 기본 피해
        self.slam_ratio = cfg.get('slam_ratio', 0.1)       # 병사 수 비례 피해
        self.fan_count = cfg.get('fan_count', 7)
        self.pattern = self.patterns[0]
        self.pattern_i = 0
        self.warn_x = self.x
        self.t = 0.0
        self.mouth = 0.0
        self.hit_t = 0.0
        self.phase = 0.0
        self.speed_scale = 1.0
        self.image = assets.image('boss.png')
        self.sm = StateMachine(self)
        self.sm.start(Enter)
        self.sm.set_transitions({
            Enter: {event_is('ARRIVED'): Idle},
            Idle: {event_is('TIMEOUT'): Warn, event_is('DIED'): Dead},
            Warn: {event_is('TIMEOUT'): Attack, event_is('DIED'): Dead},
            Attack: {event_is('TIMEOUT'): Cooldown, event_is('DIED'): Dead},
            Cooldown: {event_is('TIMEOUT'): Idle, event_is('DIED'): Dead},
            Dead: {},
        })

    def arrived(self):
        return self.sm.cur_state is not Enter

    def is_dying(self):
        return self.sm.cur_state is Dead

    # ---- 갱신
    def update(self):
        dt = game_framework.frame_time
        self.hit_t = max(0.0, self.hit_t - dt)
        self.mouth = max(0.0, self.mouth - dt)
        self.speed_scale = 1.5 if self.hp <= self.max_hp * 0.5 else 1.0     # HP 50% 이하: 패턴 속도 증가
        self.sm.update()

    def bob(self):
        self.phase += game_framework.frame_time * 3
        self.y = STOP_Y + 6 * math.sin(self.phase)

    # ---- 패턴
    def do_slam(self):
        """내려찍기: 경고 구역과 겹치는 만큼 병사 감소."""
        fx.flash(0.35)
        fx.pop(self.warn_x, 330, 'white', 220)
        sq = game_world.player
        if not sq or sq.n <= 0:
            return
        r = sq.radius()
        lo = max(sq.x - r, self.warn_x - self.SLAM_W / 2)
        hi = min(sq.x + r, self.warn_x + self.SLAM_W / 2)
        frac = max(0.0, hi - lo) / (2 * r)
        if frac > 0:
            sq.take(max(1, math.ceil(frac * (self.slam_base + sq.n * self.slam_ratio))))

    def do_fan(self):
        n = self.fan_count
        for i in range(n):
            ang = math.radians(-55 + 110 * i / (n - 1))
            sp = 270
            spawn_enemy_bullet(self.x, self.y - 70, math.sin(ang) * sp, -math.cos(ang) * sp)

    def do_summon(self):
        for i in range(6):
            x = config.BRIDGE_L + 40 + (config.BRIDGE_R - config.BRIDGE_L - 80) * i / 5
            g = Grunt(x, self.y - 100 - (i % 2) * 24, march=110)
            game_world.add_object(g, 1)
            game_world.add_collision_pair('bullet:enemy', None, g)
            game_world.add_collision_pair('squad:enemy', None, g)

    # ---- 그리기
    def draw_body(self, alpha=1.0):
        frame = 1 if self.mouth > 0 else 0
        s = self.SIZE * (1.04 if self.hit_t > 0 else 1.0)
        if alpha < 1.0:
            self.image.opacify(alpha)
        self.image.clip_draw(frame * 220, 0, 220, 220, self.x, self.y, s, s)
        if alpha < 1.0:
            self.image.opacify(1.0)

    def draw(self):
        self.sm.draw()
        if self.sm.cur_state is not Dead:
            w = 280
            ratio = max(0.0, self.hp / self.max_hp)
            ui.draw_img('px_black.png', self.x, self.y + 122, w + 8, 22, alpha=0.85)
            ui.draw_img('px_red.png', self.x - w / 2 + w * ratio / 2, self.y + 122, max(1, w * ratio), 14)

    def get_bb(self):
        r = self.SIZE * 0.45
        return self.x - r, self.y - r, self.x + r, self.y + r

    def handle_collision(self, group, other):
        if group == 'bullet:boss' and self.arrived() and not self.is_dying():
            self.hp -= other.damage
            self.hit_t = 0.06
            if self.hp <= 0:
                self.hp = 0
                self.sm.handle_event(('DIED', 0))
