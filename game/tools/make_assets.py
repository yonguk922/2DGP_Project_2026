"""게임 이미지 리소스를 코드로 생성하는 스크립트 (PIL 사용).

실행:  python tools/make_assets.py
결과:  assets/*.png
- 4배 크게 그린 뒤 줄여서(슈퍼샘플링) 가장자리를 부드럽게 만든다.
- 한글 문구는 pico2d 폰트가 한글을 못 그리므로 PNG 이미지로 미리 만들어 둔다.
"""
import os
import shutil
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(__file__), '..', 'assets')
os.makedirs(OUT, exist_ok=True)
SS = 4  # 슈퍼샘플링 배율

NAVY = (21, 25, 46)
CREAM = (246, 242, 232)
YELLOW = (255, 210, 63)
BLUE = (74, 139, 255)
BLUE_D = (30, 70, 160)
RED = (232, 90, 60)
RED_D = (130, 35, 25)
CORAL = (255, 107, 91)
SEA = (43, 92, 158)
ROAD = (144, 150, 166)


def canvas(w, h):
    return Image.new('RGBA', (w * SS, h * SS), (0, 0, 0, 0))


def finish(img, name):
    w, h = img.size[0] // SS, img.size[1] // SS
    img.resize((w, h), Image.LANCZOS).save(os.path.join(OUT, name))


def circ(d, cx, cy, r, fill, outline=None, width=2):
    d.ellipse([(cx - r) * SS, (cy - r) * SS, (cx + r) * SS, (cy + r) * SS],
              fill=fill, outline=outline, width=width * SS if outline else 0)


def rect(d, x0, y0, x1, y1, fill, radius=0, outline=None, width=2):
    box = [x0 * SS, y0 * SS, x1 * SS, y1 * SS]
    if radius:
        d.rounded_rectangle(box, radius=radius * SS, fill=fill, outline=outline,
                            width=width * SS if outline else 0)
    else:
        d.rectangle(box, fill=fill, outline=outline, width=width * SS if outline else 0)


# ---------------------------------------------------------------- 병사 (4프레임)
def make_soldier():
    S = 40
    img = canvas(S * 4, S)
    d = ImageDraw.Draw(img)
    swing = [-4, 0, 4, 0]
    for f in range(4):
        ox = f * S
        cx, cy = ox + S / 2, S / 2 + 2
        # 팔(손): 프레임마다 앞뒤로 흔들림
        circ(d, cx - 13, cy + swing[f], 4.5, BLUE_D)
        circ(d, cx + 13, cy - swing[f], 4.5, BLUE_D)
        # 몸통
        circ(d, cx, cy, 12, BLUE, NAVY, 2)
        # 헬멧
        circ(d, cx, cy - 1, 7, (140, 185, 255), NAVY, 1)
        # 총 (위쪽)
        rect(d, cx - 1.5, cy - 20, cx + 1.5, cy - 6, NAVY)
    finish(img, 'soldier.png')


# ---------------------------------------------------------------- 일반 적 (4프레임)
def make_grunt():
    S = 36
    img = canvas(S * 4, S)
    d = ImageDraw.Draw(img)
    bob = [0, -1.5, 0, 1.5]
    for f in range(4):
        ox = f * S
        cx, cy = ox + S / 2, S / 2 + bob[f]
        circ(d, cx - 12, cy + 3 - bob[f], 4, RED_D)
        circ(d, cx + 12, cy + 3 - bob[f], 4, RED_D)
        circ(d, cx, cy, 13, RED, NAVY, 2)
        # 화난 눈
        circ(d, cx - 5, cy + 1, 3.2, 'white')
        circ(d, cx + 5, cy + 1, 3.2, 'white')
        circ(d, cx - 5, cy + 2, 1.5, NAVY)
        circ(d, cx + 5, cy + 2, 1.5, NAVY)
        d.line([(cx - 10) * SS, (cy - 7) * SS, (cx - 2) * SS, (cy - 2) * SS], fill=NAVY, width=2 * SS)
        d.line([(cx + 10) * SS, (cy - 7) * SS, (cx + 2) * SS, (cy - 2) * SS], fill=NAVY, width=2 * SS)
    finish(img, 'enemy_grunt.png')


# ---------------------------------------------------------------- 돌진형 (4프레임)
def make_charger():
    S = 56
    img = canvas(S * 4, S)
    d = ImageDraw.Draw(img)
    pulse = [0, 1.5, 3, 1.5]
    ORANGE = (255, 150, 40)
    for f in range(4):
        ox = f * S
        cx, cy = ox + S / 2, S / 2 + 3
        # 뿔
        d.polygon([(cx - 18) * SS, (cy - 10) * SS, (cx - 10) * SS, (cy - 22 - pulse[f]) * SS,
                   (cx - 5) * SS, (cy - 10) * SS], fill=CREAM, outline=NAVY)
        d.polygon([(cx + 18) * SS, (cy - 10) * SS, (cx + 10) * SS, (cy - 22 - pulse[f]) * SS,
                   (cx + 5) * SS, (cy - 10) * SS], fill=CREAM, outline=NAVY)
        circ(d, cx, cy, 20 + pulse[f] * 0.3, ORANGE, NAVY, 2)
        circ(d, cx - 7, cy - 1, 4, 'white')
        circ(d, cx + 7, cy - 1, 4, 'white')
        circ(d, cx - 7, cy, 2, RED_D)
        circ(d, cx + 7, cy, 2, RED_D)
        d.line([(cx - 13) * SS, (cy - 9) * SS, (cx - 3) * SS, (cy - 4) * SS], fill=NAVY, width=3 * SS)
        d.line([(cx + 13) * SS, (cy - 9) * SS, (cx + 3) * SS, (cy - 4) * SS], fill=NAVY, width=3 * SS)
        rect(d, cx - 8, cy + 7, cx + 8, cy + 12, NAVY, 2)
    finish(img, 'enemy_charger.png')


# ---------------------------------------------------------------- 원거리형 (4프레임)
def make_shooter():
    S = 52
    img = canvas(S * 4, S)
    d = ImageDraw.Draw(img)
    recoil = [0, 3, 1, 0]
    PURPLE = (150, 90, 210)
    for f in range(4):
        ox = f * S
        cx, cy = ox + S / 2, S / 2 - 2
        # 포신 (아래쪽으로 발사)
        rect(d, cx - 5, cy + 6 - recoil[f], cx + 5, cy + 26 - recoil[f], NAVY, 2)
        circ(d, cx, cy, 17, PURPLE, NAVY, 2)
        circ(d, cx - 6, cy - 2, 3.5, 'white')
        circ(d, cx + 6, cy - 2, 3.5, 'white')
        circ(d, cx - 6, cy - 1, 1.6, NAVY)
        circ(d, cx + 6, cy - 1, 1.6, NAVY)
        d.line([(cx - 11) * SS, (cy - 9) * SS, (cx - 3) * SS, (cy - 5) * SS], fill=NAVY, width=2 * SS)
        d.line([(cx + 11) * SS, (cy - 9) * SS, (cx + 3) * SS, (cy - 5) * SS], fill=NAVY, width=2 * SS)
        # 모자
        rect(d, cx - 12, cy - 18, cx + 12, cy - 12, (90, 50, 140), 3, NAVY, 1)
    finish(img, 'enemy_shooter.png')


# ---------------------------------------------------------------- 보스 (2프레임)
def make_boss():
    S = 220
    img = canvas(S * 2, S)
    d = ImageDraw.Draw(img)
    for f in range(2):
        ox = f * S
        cx, cy = ox + S / 2, S / 2
        # 등 가시
        for k in range(8):
            import math
            a = math.radians(k * 45 + 22)
            r0, r1 = 88, 106 + (4 if f else 0)
            p1 = (cx + r0 * math.cos(a - 0.22), cy + r0 * math.sin(a - 0.22))
            p2 = (cx + r1 * math.cos(a), cy + r1 * math.sin(a))
            p3 = (cx + r0 * math.cos(a + 0.22), cy + r0 * math.sin(a + 0.22))
            d.polygon([(x * SS, y * SS) for x, y in (p1, p2, p3)], fill=RED_D, outline=NAVY)
        circ(d, cx, cy, 92, CORAL, NAVY, 4)
        circ(d, cx, cy + 8, 70, (255, 140, 120))
        # 눈
        for sx in (-1, 1):
            circ(d, cx + sx * 34, cy - 22, 19, 'white', NAVY, 3)
            circ(d, cx + sx * 34, cy - 18, 9, NAVY)
            d.line([(cx + sx * 56) * SS, (cy - 52) * SS, (cx + sx * 12) * SS, (cy - 36) * SS],
                   fill=NAVY, width=7 * SS)
        # 입
        if f == 0:
            rect(d, cx - 36, cy + 28, cx + 36, cy + 52, NAVY, 10)
            for t in range(-3, 4):
                d.polygon([(cx + t * 10 - 5) * SS, (cy + 28) * SS, (cx + t * 10 + 5) * SS, (cy + 28) * SS,
                           (cx + t * 10) * SS, (cy + 40) * SS], fill='white')
        else:
            rect(d, cx - 40, cy + 24, cx + 40, cy + 66, NAVY, 14)
            circ(d, cx, cy + 56, 14, RED)
            for t in range(-3, 4):
                d.polygon([(cx + t * 11 - 5) * SS, (cy + 24) * SS, (cx + t * 11 + 5) * SS, (cy + 24) * SS,
                           (cx + t * 11) * SS, (cy + 38) * SS], fill='white')
    finish(img, 'boss.png')


# ---------------------------------------------------------------- 총알 / 게이트 / 효과
def make_misc():
    img = canvas(14, 14)
    d = ImageDraw.Draw(img)
    circ(d, 7, 7, 6, YELLOW, (200, 150, 0), 1)
    finish(img, 'bullet.png')

    img = canvas(16, 16)
    d = ImageDraw.Draw(img)
    circ(d, 8, 8, 7, (255, 60, 160), NAVY, 1)
    circ(d, 8, 8, 3, (255, 200, 230))
    finish(img, 'bullet_enemy.png')

    for name, top, bot, edge in (('gate_blue.png', (90, 150, 255), (50, 110, 230), (20, 50, 130)),
                                 ('gate_red.png', (255, 190, 180), (250, 150, 140), (150, 50, 50))):
        W, H = 170, 110
        img = canvas(W, H)
        d = ImageDraw.Draw(img)
        rect(d, 2, 2, W - 2, H - 2, bot, 14, edge, 3)
        rect(d, 8, 8, W - 8, H // 2, top, 10)
        finish(img, name)

    # 경고 표시 (반투명 빨간 줄무늬)
    img = canvas(64, 64)
    d = ImageDraw.Draw(img)
    rect(d, 0, 0, 64, 64, (255, 60, 60, 255))
    for k in range(-2, 6):
        d.polygon([(k * 20) * SS, 0, (k * 20 + 10) * SS, 0, (k * 20 + 74) * SS, 64 * SS,
                   (k * 20 + 64) * SS, 64 * SS], fill=(255, 220, 220, 255))
    finish(img, 'warning.png')

    # 병사 수 말풍선(둥근 알약)
    img = canvas(120, 44)
    d = ImageDraw.Draw(img)
    rect(d, 1, 1, 119, 43, NAVY, 22, (255, 255, 255, 255), 2)
    finish(img, 'pill.png')

    # 코인
    img = canvas(24, 24)
    d = ImageDraw.Draw(img)
    circ(d, 12, 12, 11, YELLOW, (200, 150, 0), 2)
    circ(d, 12, 12, 6, (255, 235, 140))
    finish(img, 'coin.png')

    # 상단 HUD 바
    img = canvas(540, 60)
    d = ImageDraw.Draw(img)
    rect(d, 0, -30, 540, 60, (21, 25, 46, 215), 30)
    finish(img, 'hud_bar.png')

    # 단색 1x1 (HP 바 / 검은 반투명 막)
    for name, col in (('px_white.png', (255, 255, 255, 255)), ('px_black.png', (0, 0, 0, 255)),
                      ('px_red.png', CORAL + (255,)), ('px_green.png', (90, 220, 120, 255))):
        Image.new('RGBA', (4, 4), col).save(os.path.join(OUT, name))


# ---------------------------------------------------------------- 배경 (세로로 이어 붙는 타일)
def make_bridge():
    W, H = 540, 900
    img = Image.new('RGBA', (W * SS, H * SS), SEA + (255,))
    d = ImageDraw.Draw(img)
    # 바다 물결 (주기 150px → 900px 타일이 이음새 없이 이어짐)
    import random
    rnd = random.Random(7)
    for k in range(60):
        y = (k * 150 // 4 + rnd.randint(0, 30)) % H
        x = rnd.choice([rnd.randint(5, 70), rnd.randint(470, 530)])
        d.line([x * SS, y * SS, (x + 26) * SS, y * SS], fill=(90, 140, 200, 255), width=3 * SS)
    # 다리 상판
    L, R = 90, 450
    rect(d, L, 0, R, H, ROAD)
    for y in range(0, H, 60):            # 널빤지 이음선
        d.line([L * SS, y * SS, R * SS, y * SS], fill=(125, 131, 148, 255), width=2 * SS)
    # 난간
    rect(d, L - 12, 0, L, H, (212, 216, 224))
    rect(d, R, 0, R + 12, H, (212, 216, 224))
    for y in range(0, H, 90):            # 난간 기둥
        rect(d, L - 16, y + 8, L + 2, y + 26, (170, 176, 190))
        rect(d, R - 2, y + 8, R + 16, y + 26, (170, 176, 190))
    # 중앙선 (주기 180px)
    for y in range(0, H, 180):
        rect(d, 266, y + 20, 274, y + 100, CREAM)
    img.resize((W, H), Image.LANCZOS).save(os.path.join(OUT, 'bridge.png'))


# ---------------------------------------------------------------- 한글 문구 PNG
def find_kr_font(size):
    path = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
    for idx in range(6):
        f = ImageFont.truetype(path, size, index=idx)
        if 'KR' in ' '.join(f.getname()):
            return f
    return ImageFont.truetype(path, size)


def text_png(name, lines, size, pad=8):
    """lines: [(문구, 색)]  가운데 정렬 여러 줄 PNG"""
    f = find_kr_font(size)
    widths, h = [], int(size * 1.25)
    for t, _ in lines:
        widths.append(int(f.getlength(t)))
    W = max(widths) + pad * 2
    H = h * len(lines) + pad * 2
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, (t, c) in enumerate(lines):
        d.text(((W - widths[i]) / 2, pad + i * h), t, font=f, fill=c)
    img.save(os.path.join(OUT, name))


def make_texts():
    text_png('t_title.png', [('광고에서 본 그 게임,', CREAM), ('진짜임.', YELLOW)], 50)
    text_png('t_sub.png', [('설치하면 다른 게임이 나오던 그 광고,', (200, 205, 225)),
                           ('이번엔 진짜로 끝까지 플레이할 수 있습니다', (200, 205, 225))], 22)
    text_png('t_start.png', [('Enter 또는 클릭으로 시작', YELLOW)], 28)
    text_png('t_help.png', [('← → / A D / 마우스 드래그로 이동', CREAM), ('사격은 자동! 게이트를 쏴서 숫자를 바꿔 보세요', CREAM)], 20)
    text_png('t_gameover.png', [('게임 오버', (255, 107, 91))], 64)
    text_png('t_clear.png', [('스테이지 클리어!', YELLOW)], 54)
    text_png('t_allclear.png', [('게임 클리어!', YELLOW)], 60)
    text_png('t_next.png', [('Enter : 다음 스테이지', CREAM)], 26)
    text_png('t_retry.png', [('Enter : 다시 도전', CREAM)], 26)
    text_png('t_totitle.png', [('Enter : 타이틀로', CREAM)], 26)
    text_png('t_pause.png', [('일시정지', CREAM), ('ESC : 계속하기', YELLOW)], 40)
    text_png('t_boss.png', [('보스 등장!', (255, 107, 91))], 44)
    text_png('t_label_soldier.png', [('남은 병사', CREAM)], 20)
    text_png('t_label_coin.png', [('획득 코인', CREAM)], 20)
    text_png('t_label_best.png', [('최고 기록', CREAM)], 20)
    text_png('t_stage.png', [('스테이지', CREAM)], 20)
    text_png('t_select.png', [('1 · 2 · 3 : 스테이지 선택', (200, 205, 225))], 20)
    text_png('t_upgrade.png', [('U : 시작 병사 +5 업그레이드', CREAM)], 22)
    text_png('t_label_start.png', [('시작 병사', (200, 205, 225))], 20)
    text_png('t_label_cost.png', [('비용', (200, 205, 225))], 20)
    text_png('t_maxlv.png', [('최대 레벨', YELLOW)], 20)
    text_png('t_label_coins_have.png', [('보유 코인', (200, 205, 225))], 20)


# ---------------------------------------------------------------- 숫자 비트맵 폰트
GLYPHS = '0123456789+\u2212\u00d7\u00f7/:%'   # 0-9 + − × ÷ / : %
GW, GH = 40, 56


def make_digits():
    """pico2d의 Font.draw는 호출할 때마다 텍스처를 만들어 메모리가 새므로,
    숫자는 미리 만든 글자 시트(digits_*.png)를 clip_draw로 그린다."""
    f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 44)
    for name, col in (('white', (255, 255, 255)), ('yellow', YELLOW), ('navy', NAVY), ('red', CORAL)):
        img = Image.new('RGBA', (GW * len(GLYPHS), GH), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        for i, ch in enumerate(GLYPHS):
            w = d.textlength(ch, font=f)
            d.text((i * GW + (GW - w) / 2, 2), ch, font=f, fill=col + (255,))
        img.save(os.path.join(OUT, f'digits_{name}.png'))


def make_fx():
    for name, col in (('red', RED), ('blue', BLUE), ('white', (255, 255, 255))):
        img = canvas(64, 64)
        d = ImageDraw.Draw(img)
        d.ellipse([4 * SS, 4 * SS, 60 * SS, 60 * SS], outline=col + (255,), width=6 * SS)
        for k in range(8):
            import math
            a = k * math.pi / 4
            circ(d, 32 + 20 * math.cos(a), 32 + 20 * math.sin(a), 4, col + (255,))
        finish(img, f'fx_pop_{name}.png')


if __name__ == '__main__':
    make_soldier()
    make_grunt()
    make_charger()
    make_shooter()
    make_boss()
    make_misc()
    make_bridge()
    make_texts()
    make_digits()
    make_fx()
    print('assets done:', len(os.listdir(OUT)))
