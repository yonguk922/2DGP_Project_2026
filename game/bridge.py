"""다리 배경: 세로로 이어 붙인 타일을 카메라 거리만큼 스크롤."""
import assets
import config
import game_world


class Bridge:
    def __init__(self):
        self.image = assets.image('bridge.png')

    def update(self):
        pass

    def draw(self):
        off = game_world.distance % config.H
        self.image.draw(config.W / 2, config.H / 2 - off)
        self.image.draw(config.W / 2, config.H / 2 - off + config.H)
