"""이펙트: 터지는 링(pop), 떠오르는 숫자(text), 화면 번쩍임(flash), 배너."""
import assets
import config
import game_framework
import game_world
import ui


class Fx:
    def __init__(self, kind, x, y, life=0.4, **kw):
        self.kind = kind
        self.x, self.y = x, y
        self.life = self.max_life = life
        self.kw = kw

    def update(self):
        self.life -= game_framework.frame_time
        if self.life <= 0:
            game_world.remove_object(self)

    def draw(self):
        t = 1.0 - self.life / self.max_life          # 0 → 1
        k = self.kind
        if k == 'pop':
            size = self.kw.get('size', 60) * (0.4 + 0.9 * t)
            ui.draw_img(self.kw['img'], self.x, self.y, size, size, alpha=max(0.0, 1 - t))
        elif k == 'text':
            ui.text(self.kw['s'], self.x, self.y + 50 * t, self.kw.get('h', 40),
                    self.kw.get('color', 'yellow'), alpha=max(0.0, 1.0 - t * t))
        elif k == 'flash':
            ui.draw_img('px_white.png', config.W / 2, config.H / 2, config.W, config.H,
                        alpha=self.kw.get('a', 0.5) * (1 - t))
        elif k == 'banner':
            a = 1.0 if t < 0.7 else (1 - t) / 0.3
            ui.draw_img(self.kw['img'], config.W / 2, self.y, alpha=max(0.0, a))


def pop(x, y, color='red', size=60):
    game_world.add_object(Fx('pop', x, y, 0.35, img='fx_pop_%s.png' % color, size=size), 4)


def float_text(x, y, s, color='yellow', h=40):
    game_world.add_object(Fx('text', x, y, 0.9, s=s, color=color, h=h), 4)


def flash(a=0.5):
    game_world.add_object(Fx('flash', 0, 0, 0.3, a=a), 4)


def banner(img, y, life=1.8):
    game_world.add_object(Fx('banner', 0, y, life, img=img), 4)
