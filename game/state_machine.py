"""수업 시간에 배운 상태 머신 (이벤트 큐 + 전이 표)."""


def event_is(name):
    return lambda e: e[0] == name


class StateMachine:
    def __init__(self, obj):
        self.obj = obj
        self.event_q = []
        self.cur_state = None
        self.transitions = {}

    def start(self, state):
        self.cur_state = state
        self.cur_state.enter(self.obj, ('START', 0))

    def set_transitions(self, transitions):
        self.transitions = transitions

    def add_event(self, e):
        self.event_q.append(e)

    def update(self):
        self.cur_state.do(self.obj)
        if self.event_q:
            self.handle_event(self.event_q.pop(0))

    def handle_event(self, e):
        for check, next_state in self.transitions.get(self.cur_state, {}).items():
            if check(e):
                self.cur_state.exit(self.obj, e)
                self.cur_state = next_state
                self.cur_state.enter(self.obj, e)
                return

    def draw(self):
        self.cur_state.draw(self.obj)
