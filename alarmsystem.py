
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


list_of_states = [Disarmed(), Armed(), Warning(), Alarm()]

state = list_of_states[0].process_event(EventType.arm)
state = list_of_states[state.value].process_event(EventType.disarm)
state = list_of_states[state.value].process_event(EventType.arm)
state = list_of_states[state.value].process_event(EventType.sensor_tripped)

print(state)
