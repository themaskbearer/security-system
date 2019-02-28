
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
    def __init__(self):
        self._transitions = {}

    def process_event(self, event):
        if event in self._transitions:
            return self._transitions[event]
        else:
            return 0

    def add_transition(self, event, state):
        self._transitions[event] = state


class Disarmed(State):
    def __init__(self):
        State.__init__(self)
        self.add_transition(EventType.arm, StateType.armed)


class Armed(State):
    def __init__(self):
        State.__init__(self)
        self.add_transition(EventType.disarm, StateType.disarmed)
        self.add_transition(EventType.sensor_tripped, StateType.warning)


class Warning(State):
    def __init__(self):
        State.__init__(self)
        self.add_transition(EventType.disarm, StateType.disarmed)
        self.add_transition(EventType.warning_expired, StateType.alarm)


class Alarm(State):
    def __init__(self):
        State.__init__(self)
        self.add_transition(EventType.disarm, StateType.disarmed)


class AlarmSystem:
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
