
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class EventType(Enum):
    arm = 1
    disarm = 2
    sensor_changed = 3
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

    def on_entry(self):
        logger.info("State %s on_entry", type(self).__name__)
        pass

    def on_exit(self):
        logger.info("State %s on_exit", type(self).__name__)
        pass


class Disarmed(State):
    def __init__(self):
        State.__init__(self, StateType.disarmed)
        self.add_transition(EventType.arm, StateType.armed)

    def process_event(self, event):
        # Process door chime

        return State.process_event(self, event)


class Armed(State):
    def __init__(self):
        State.__init__(self, StateType.armed)
        self.add_transition(EventType.disarm, StateType.disarmed)
        self.add_transition(EventType.sensor_changed, StateType.warning)

    def process_event(self, event):
        # Process if sensor that was tripped should trigger alarm
        # Return back StateType.armed if ignoring the sensor
        # - i.e. motion sensor during Arm.stay

        return State.process_event(self, event)


class Warning(State):
    def __init__(self):
        State.__init__(self, StateType.warning)
        self.add_transition(EventType.disarm, StateType.disarmed)
        self.add_transition(EventType.warning_expired, StateType.alarm)

    def on_entry(self):
        # turn on warning beep
        # Start timer
        State.on_entry(self)

    def on_exit(self):
        # turn off warning beep
        # Disable timer
        State.on_exit(self)


class Alarm(State):
    def __init__(self):
        State.__init__(self, StateType.alarm)
        self.add_transition(EventType.disarm, StateType.disarmed)

    def on_entry(self):
        # turn on alarm
        State.on_entry(self)

    def on_exit(self):
        # turn off alarm
        State.on_exit(self)


class AlarmStateMachine:
    def __init__(self):
        self._state_machine = {StateType.disarmed: Disarmed(),
                               StateType.armed: Armed(),
                               StateType.warning: Warning(),
                               StateType.alarm: Alarm()}

        self._current_state = StateType.disarmed
        self._state_machine[self._current_state].on_entry()

    def get_current_state(self):
        return self._current_state

    def get_zone_status(self):
        pass

    def process_event(self, event):
        new_state = self._state_machine[self._current_state].process_event(event)

        if self._current_state != new_state:
            self._state_machine[self._current_state].on_exit()
            self._state_machine[new_state].on_entry()
            self._current_state = new_state

        return self._current_state

    @staticmethod
    def is_valid_external_event(event):
        if event == EventType.disarm or event == EventType.arm:
            return True
        else:
            return False
