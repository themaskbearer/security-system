
from enum import Enum


class EventType(Enum):
    arm = 1
    disarm = 2
    sensor_tripped = 3
    warning_expired = 4


class StateType(Enum):
    disarmed = 0
    armed = 1
    warning = 2
    alarm = 3


class State:
    def __init__(self, self_state):
        self._transitions = {}
        self._self_state = self_state

    def process_event(self, event):
        if event in self._transitions:
            return self._transitions[event]
        else:
            return self._self_state

    def add_transition(self, event, state):
        self._transitions[event] = state


class Disarmed(State):
    def __init__(self):
        State.__init__(self, StateType.disarmed)
        self.add_transition(EventType.arm, StateType.armed)


class Armed(State):
    def __init__(self):
        State.__init__(self, StateType.armed)
        self.add_transition(EventType.disarm, StateType.disarmed)
        self.add_transition(EventType.sensor_tripped, StateType.warning)


class Warning(State):
    def __init__(self):
        State.__init__(self, StateType.warning)
        self.add_transition(EventType.disarm, StateType.disarmed)
        self.add_transition(EventType.warning_expired, StateType.alarm)


class Alarm(State):
    def __init__(self):
        State.__init__(self, StateType.alarm)
        self.add_transition(EventType.disarm, StateType.disarmed)


class AlarmStateMachine:
    def __init__(self):
        self._state_machine = {StateType.disarmed: Disarmed(),
                               StateType.armed: Armed(),
                               StateType.warning: Warning(),
                               StateType.alarm: Alarm()}
        self._current_state = StateType.disarmed

    def get_current_state(self):
        return self._current_state

    def get_zone_status(self):
        pass

    def process_event(self, event):
        self._current_state = self._state_machine[self._current_state].process_event(event)
        return self._current_state

    @staticmethod
    def is_valid_external_event(event):
        if event == EventType.disarm or event == EventType.arm:
            return True
        else:
            return False
