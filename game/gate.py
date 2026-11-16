"""숫자 게이트. 두 개 1조로 나오며, 총알을 맞히면 값이 바뀐다."""
import assets
import config
import game_framework
import game_world
import fx
import ui

FLIP_HITS = 30       # ÷ 게이트는 이 횟수만큼 맞히면 × 게이트로 뒤집힌다
MAX_BONUS = 25       # +/− 게이트는 총알로 최대 +25까지만 올라간다 (병사가 많을 때 무한 증가 방지)
HITTABLE_Y = 780     # 화면 위쪽에 막 나타난 게이트는 아직 맞지 않는다


class Gate:
    W, H = 170, 110

    def __init__(self, x, y, op, value):
        self.x, self.y = x, y
        self.op = op              # 'add'(부호 있는 값) / 'mul' / 'div'
        self.value = value
        self.hits = 0
        self.used = False
        self.partner = None
        self.fade = 1.0

    # ---- 값 / 표시
    def is_good(self):
        if self.op == 'add':
            return self.value >= 0
        return self.op == 'mul'

    def label(self):
        if self.op == 'add':
            return ('+%d' if self.value >= 0 else '−%d') % abs(self.value)
        return ('×%d' if self.op == 'mul' else '÷%d') % self.value

    def apply(self, n):
        if self.op == 'add':
            return max(0, n + self.value)
        if self.op == 'mul':
            return n * self.value
        return n // self.value          # 연산 결과는 정수로 내림

    # ---- 게임 루프
    def update(self):
        dt = game_framework.frame_time
        self.y -= game_world.scroll_speed * dt
        if self.used:
            self.fade -= dt * 4
            if self.fade <= 0:
                game_world.remove_object(self)
            return
        if self.y < -80:
            game_world.remove_object(self)
            return
        sq = game_world.player
        # 통과 판정: 무리의 중심이 게이트 안에 들어오면 한 번만 연산 적용
        if sq and sq.alive_for_gate() and abs(self.y - sq.y) < self.H / 2 and abs(sq.x - self.x) < self.W / 2:
            self.pass_through(sq)

    def pass_through(self, sq):
        before = sq.n
        sq.n = self.apply(before)
        diff = sq.n - before
        good = diff >= 0
        fx.float_text(sq.x, sq.y + 90, self.label(), 'yellow' if good else 'red', 44)
        fx.pop(sq.x, sq.y, 'blue' if good else 'red', 160)
        self.disable()
        if self.partner:
            self.partner.disable()
        if sq.n <= 0:
            sq.kill()

    def disable(self):
        self.used = True
        game_world.remove_collision_object(self)

    def draw(self):
        a = max(0.0, self.fade)
        img = 'gate_blue.png' if self.is_good() else 'gate_red.png'
        ui.draw_img(img, self.x, self.y, self.W, self.H, alpha=a)
        color = 'white' if self.is_good() else 'navy'
        ui.text(self.label(), self.x, self.y - 6, 54, color, alpha=a)
        if self.op == 'div' and not self.used:           # 뒤집히기까지 진행도 표시
            ratio = self.hits / FLIP_HITS
            ui.draw_img('px_black.png', self.x, self.y - 44, 120, 6, alpha=0.5)
            ui.draw_img('px_green.png', self.x - 60 + 60 * ratio, self.y - 44, 120 * ratio + 0.01, 6)

    def get_bb(self):
        return self.x - self.W / 2, self.y - self.H / 2, self.x + self.W / 2, self.y + self.H / 2

    def handle_collision(self, group, other):
        if group == 'bullet:gate' and not self.used and self.y < HITTABLE_Y:
            self.hits += 1
            if self.op == 'add':
                if self.hits <= MAX_BONUS:
                    self.value += 1                       # −15 → −14 → … → +5
            elif self.op == 'div' and self.hits >= FLIP_HITS:
                self.op = 'mul'                       # ÷2 → ×2
                fx.pop(self.x, self.y, 'white', 140)
