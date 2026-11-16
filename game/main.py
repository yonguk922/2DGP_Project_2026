"""진입점:  python main.py"""
from pico2d import open_canvas, close_canvas

import config
import game_framework
import title_mode

open_canvas(config.W, config.H)
game_framework.run(title_mode)
close_canvas()
