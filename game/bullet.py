"""병사의 총알 / 적의 탄."""
import assets
import config
import game_framework
import game_world


class Bullet:
    """병사가 쏘는 총알. 위로 날아가며 적·게이트·보스에 맞으면 사라진다."""

    def __init__(self, x, y, damage=1):
        self.x, self.y = x, y
        self.vy = 720.0
        self.damage = damage
        self.image = assets.image('bullet.png')

    def update(self):
        self.y += self.vy * game_framework.frame_time
        if self.y > config.H + 20:
            game_world.remove_object(self)

    def draw(self):
        self.image.draw(self.x, self.y)

    def get_bb(self):
        return self.x - 5, self.y - 6, self.x + 5, self.y + 8

    def handle_collision(self, group, other):
        if group in ('bullet:enemy', 'bullet:gate', 'bullet:boss'):
            game_world.remove_object(self)


class EnemyBullet:
    """원거리형 적·보스가 쏘는 탄. 병사에 맞으면 병사 1명 감소."""

    def __init__(self, x, y, vx, vy, damage=1):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.damage = damage
        self.image = assets.image('bullet_enemy.png')

    def update(self):
        dt = game_framework.frame_time
        self.x += self.vx * dt
        self.y += (self.vy - game_world.scroll_speed) * dt
        if self.y < -30 or self.y > config.H + 80 or self.x < -30 or self.x > config.W + 30:
            game_world.remove_object(self)

    def draw(self):
        self.image.draw(self.x, self.y, 20, 20)

    def get_bb(self):
        return self.x - 7, self.y - 7, self.x + 7, self.y + 7

    def handle_collision(self, group, other):
        if group == 'squad:ebullet':
            game_world.remove_object(self)


def spawn_enemy_bullet(x, y, vx, vy):
    """적 탄을 월드와 충돌 그룹에 한 번에 등록."""
    b = EnemyBullet(x, y, vx, vy)
    game_world.add_object(b, 2)
    game_world.add_collision_pair('squad:ebullet', None, b)
    return b
