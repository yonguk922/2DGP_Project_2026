"""적 3종: 일반 무리(Grunt) / 돌진형(Charger) / 원거리형(Shooter)."""
import math
import random

import assets
import config
import fx
import game_framework
import game_world
from bullet import spawn_enemy_bullet


class Enemy:
    IMG = 'enemy_grunt.png'
    CELL = 36
    SIZE = 32
    HP = 1
    DAMAGE = 1
    COIN = 1
    FPS = 8

    def __init__(self, x, y):
        self.x, self.y = x, y
        self.hp = self.HP
        self.frame = random.random() * 4
        self.image = assets.image(self.IMG)
        self.hit_t = 0.0

    def update(self):
        dt = game_framework.frame_time
        self.frame = (self.frame + self.FPS * dt) % 4
        self.hit_t = max(0.0, self.hit_t - dt)
        self.y -= game_world.scroll_speed * dt
        self.behave(dt)
        if self.y < -60:
            game_world.remove_object(self)

    def behave(self, dt):
        pass

    def draw(self):
        s = self.SIZE * (1.15 if self.hit_t > 0 else 1.0)
        self.image.clip_draw(int(self.frame) * self.CELL, 0, self.CELL, self.CELL, self.x, self.y, s, s)

    def get_bb(self):
        r = self.SIZE * 0.42
        return self.x - r, self.y - r, self.x + r, self.y + r

    def die(self):
        fx.pop(self.x, self.y, 'red', self.SIZE * 2)
        game_world.stats['kills'] += 1
        game_world.stats['coins'] += self.COIN
        game_world.remove_object(self)

    def handle_collision(self, group, other):
        if group == 'bullet:enemy':
            self.hp -= other.damage
            self.hit_t = 0.08
            if self.hp <= 0:
                self.die()
        elif group == 'squad:enemy':
            # 병사와 부딪히면 함께 소멸 (병사는 DAMAGE명 감소)
            other.take(self.DAMAGE)
            self.die()


class Grunt(Enemy):
    """다리 위에 무리 지어 서 있다가, 가까워지면 정면으로 다가온다."""
    MARCH = 80

    def __init__(self, x, y, march=None):
        super().__init__(x, y)
        self.march = self.MARCH if march is None else march
        self.always = march is not None

    def behave(self, dt):
        if self.always or self.y < 620:
            self.y -= self.march * dt


class Charger(Enemy):
    """병사 무리의 x 위치를 추적하며 빠르게 돌진 (규칙 기반 AI: 거리 안이면 추적)."""
    IMG = 'enemy_charger.png'
    CELL = 56
    SIZE = 52
    HP = 3
    DAMAGE = 3
    COIN = 3
    SIGHT = 720

    def behave(self, dt):
        sq = game_world.player
        if sq and self.y < self.SIGHT:
            dx = sq.x - self.x
            self.x += max(-170 * dt, min(170 * dt, dx))
            self.y -= 130 * dt
        self.x = max(config.BRIDGE_L + 20, min(config.BRIDGE_R - 20, self.x))


class Shooter(Enemy):
    """다리 양옆에서 무리를 향해 탄을 발사 (사거리 안이면 사격)."""
    IMG = 'enemy_shooter.png'
    CELL = 52
    SIZE = 48
    HP = 5
    DAMAGE = 1
    COIN = 5
    FPS = 4

    def __init__(self, x, y):
        super().__init__(x, y)
        self.cool = 0.8

    def behave(self, dt):
        sq = game_world.player
        self.cool -= dt
        if sq and self.cool <= 0 and 250 < self.y < config.H - 40:
            dx, dy = sq.x - self.x, sq.y - self.y
            d = math.hypot(dx, dy) or 1
            sp = 300
            spawn_enemy_bullet(self.x, self.y - 20, dx / d * sp, dy / d * sp)
            self.cool = 1.4


KINDS = {'grunt': Grunt, 'charger': Charger, 'shooter': Shooter}
