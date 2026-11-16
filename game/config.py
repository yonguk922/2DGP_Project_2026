"""게임 전역 설정값."""
import os

W, H = 540, 900                  # 세로형 창 (모바일 광고 화면 느낌)
BRIDGE_L, BRIDGE_R = 90, 450     # 다리 상판의 좌우 경계
SQUAD_Y = 150                    # 병사 무리의 화면 y 위치 (고정, 다리가 스크롤됨)
BASE = os.path.dirname(os.path.abspath(__file__))


def asset(name):
    return os.path.join(BASE, 'assets', name)


def data_path(name):
    return os.path.join(BASE, 'data', name)
