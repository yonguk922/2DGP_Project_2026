"""게임 월드: 레이어별 오브젝트 관리 + 충돌 그룹 + 카메라(스크롤) 값."""

LAYERS = 5   # 0 배경 / 1 게이트·적 / 2 병사·총알 / 3 보스 / 4 UI·이펙트
layers = [[] for _ in range(LAYERS)]
collision_pairs = {}

# 카메라: 다리가 아래로 스크롤되는 속도와 누적 거리
scroll_speed = 0.0
distance = 0.0
player = None            # 병사 무리 (게이트 통과 판정, 적 AI에서 참조)
boss = None
stats = {'kills': 0, 'coins': 0}


def reset():
    global scroll_speed, distance, player, boss
    clear()
    scroll_speed = 0.0
    distance = 0.0
    player = None
    boss = None
    stats['kills'] = 0
    stats['coins'] = 0


def add_object(o, depth=0):
    o._removed = False
    layers[depth].append(o)


def add_objects(ol, depth=0):
    for o in ol:
        add_object(o, depth)


def remove_object(o):
    o._removed = True
    for layer in layers:
        if o in layer:
            layer.remove(o)
    remove_collision_object(o)


def clear():
    for layer in layers:
        layer.clear()
    collision_pairs.clear()


def update():
    for layer in layers:
        for o in layer[:]:
            if not getattr(o, '_removed', False):
                o.update()


def render():
    for layer in layers:
        for o in layer:
            o.draw()


def objects_in(depth):
    return layers[depth]


# ---------------------------------------------------------------- 충돌
def add_collision_pair(group, a, b):
    if group not in collision_pairs:
        collision_pairs[group] = [[], []]
    if a:
        collision_pairs[group][0].append(a)
    if b:
        collision_pairs[group][1].append(b)


def remove_collision_object(o):
    for pairs in collision_pairs.values():
        if o in pairs[0]:
            pairs[0].remove(o)
        if o in pairs[1]:
            pairs[1].remove(o)


def collide(a, b):
    la, ba, ra, ta = a.get_bb()
    lb, bb, rb, tb = b.get_bb()
    return not (ra < lb or la > rb or ta < bb or ba > tb)


def handle_collisions():
    for group, pairs in collision_pairs.items():
        for a in pairs[0][:]:
            if a._removed:
                continue
            for b in pairs[1][:]:
                if b._removed or a._removed:
                    continue
                if collide(a, b):
                    a.handle_collision(group, b)
                    b.handle_collision(group, a)
