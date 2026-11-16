"""숫자 비트맵 폰트 출력.  (pico2d Font.draw는 호출마다 텍스처가 쌓여 쓰지 않음)"""
import assets

GLYPHS = '0123456789+−×÷/:%'
CELL_W, CELL_H = 40, 56


def text(s, x, y, h=32, color='white', align='center', alpha=1.0):
    img = assets.image('digits_%s.png' % color)
    adv = h * 0.6
    gw = h * CELL_W / CELL_H
    total = adv * len(s)
    if align == 'center':
        cx = x - total / 2 + adv / 2
    elif align == 'left':
        cx = x + adv / 2
    else:
        cx = x - total + adv / 2
    if alpha < 1.0:
        img.opacify(alpha)
    for ch in s:
        i = GLYPHS.find(ch)
        if i >= 0:
            img.clip_draw(i * CELL_W, 0, CELL_W, CELL_H, cx, y, gw, h)
        cx += adv
    if alpha < 1.0:
        img.opacify(1.0)


def draw_img(name, x, y, w=None, h=None, alpha=1.0):
    img = assets.image(name)
    if alpha < 1.0:
        img.opacify(alpha)
    if w is None:
        img.draw(x, y)
    else:
        img.draw(x, y, w, h)
    if alpha < 1.0:
        img.opacify(1.0)
