"""상단 UI: 스테이지 / 코인 / 진행도 바."""
import assets
import config
import game_world
import ui


class Hud:
    def __init__(self, stage_no, boss_at):
        self.stage_no = stage_no
        self.boss_at = boss_at

    def update(self):
        pass

    def draw(self):
        W, H = config.W, config.H
        ui.draw_img('hud_bar.png', W / 2, H - 30)
        ui.draw_img('t_stage.png', 76, H - 28)
        ui.text(str(self.stage_no), 138, H - 28, 30, 'white')
        ui.draw_img('coin.png', W - 120, H - 28)
        ui.text(str(game_world.stats['coins']), W - 100, H - 28, 30, 'yellow', align='left')
        # 진행도 바 (보스까지 남은 거리)
        ratio = max(0.0, min(1.0, game_world.distance / self.boss_at))
        ui.draw_img('px_black.png', W / 2, H - 66, 360, 8, alpha=0.6)
        ui.draw_img('px_green.png', W / 2 - 180 + 180 * ratio, H - 66, max(1, 360 * ratio), 8)
