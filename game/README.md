# 광고에서 본 그 게임, 진짜임 (2D 게임 프로그래밍)

병사 수를 게이트로 불려 보스를 쓰러뜨리는 세로 스크롤 러너 슈팅. Python 3 + pico2d.

## 실행
```
pip install pico2d
python main.py
```
- 조작: ← → / A D / 마우스 드래그로 이동, 사격은 자동, ESC 일시정지
- 타이틀: Enter 시작 · 1/2/3 스테이지 선택 · U 시작 병사 업그레이드(코인)

## 구조
| 파일 | 역할 |
|---|---|
| main.py, game_framework.py | 진입점, 모드 전환·메인 루프 |
| title_mode / play_mode / result_mode | 화면(모드) |
| game_world.py | 레이어 관리, 충돌 그룹, 카메라 스크롤 값 |
| state_machine.py | 상태 머신 (Squad: RUN/FIGHT/WIN/DEAD, Boss: ENTER/IDLE/WARN/ATTACK/COOLDOWN/DEAD) |
| squad, bullet, gate, enemy, boss, bridge, hud, fx | 게임 오브젝트 |
| data/stage_N.json | 스테이지 데이터 (tools/make_stages.py 로 생성) |
| tools/make_assets.py | 이미지 리소스 생성 (Pillow) |
| tests/headless_test.py | 창 없이 봇이 자동 플레이 · 스크린샷 |

## 진행 상황
1~5주차 완료, 6주차 진행 중(난이도 조정), 7주차 일부(사운드 미구현), 8주차 예정. 자세한 내용은 docs/ 발표자료 참고.
