"""모드(화면) 전환과 메인 루프."""
import time

running = False
stack = []
frame_time = 1 / 60
TARGET = 1 / 60


def change_mode(mode):
    global stack
    if stack:
        stack[-1].finish()
        stack.pop()
    stack.append(mode)
    mode.init()


def quit():
    global running
    running = False


def run(start_mode):
    global running, frame_time
    from pico2d import delay
    running = True
    stack.append(start_mode)
    start_mode.init()
    prev = time.time()
    while running:
        stack[-1].handle_events()
        stack[-1].update()
        stack[-1].draw()
        now = time.time()
        spent = now - prev
        if spent < TARGET:
            delay(TARGET - spent)
            now = time.time()
        frame_time = min(now - prev, 0.05)     # 창을 끌 때 등 큰 값 방지
        prev = now
    while stack:
        stack[-1].finish()
        stack.pop()
