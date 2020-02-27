
from enum import Enum
import logging
import threading

import sensors

logger = logging.getLogger(__name__)


def load_state_configurations(config):
    global alert_timeout_s
    alert_timeout_s = config['alert'].getint('duration_s')
    arm_configurations.load_from_config(config)


class ArmConfigurations:
    def __init__(self):
        self.configurations = {}
        self.current_configuration = ''

    def load_from_config(self, config):
        config_names = config['arm_configs'].get('configurations')
        config_name_list = config_names.split(',')

        for name in config_name_list:
            new_arm_config = ArmConfiguration(name, config[name])
            self.configurations[name] = new_arm_config

    def get_current_configuration(self):
        return self.configurations[self.current_configuration]


class ArmConfiguration:
    def __init__(self, name, config):
        self.name = name
        self.zones = {}

        sensors_str = config.get('sensors')
        sensor_list = sensors_str.split(',')
        self.sensors = sensor_list

        for sensor in sensor_list:
            zones = config.get(sensor + "_zones")
            zone_list = zones.split(',')
            zone_list = map(int, zone_list)
            self.zones[sensor] = list(zone_list)


def is_valid_arm_config(config):
    if config in arm_configurations.configurations:
        return True
    return False


class EventType(Enum):
    arm = 1
    disarm = 2
    sensor_changed = 3
    alert_expired = 4


class StateType(Enum):
    disarmed = 0
    armed = 1
    alert = 2
    alarm = 3


class State:
    def __init__(self, self_state):
        self._transitions = {}
        self._self_state = self_state

    def process_event(self, event, data):
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

    def process_event(self, event, data):
        if event == EventType.arm:
            arm_configurations.current_configuration = data
        elif event == EventType.sensor_changed:
            sensors.sensor_list[data.sensor_id].zones[data.zone_number].process_door_chime()

        return State.process_event(self, event, data)


class Armed(State):
    def __init__(self):
        State.__init__(self, StateType.armed)
        self.add_transition(EventType.disarm, StateType.disarmed)
        self.add_transition(EventType.sensor_changed, StateType.alert)

    def process_event(self, event, data):
        if event == EventType.sensor_changed:
            current_arm_config = arm_configurations.get_current_configuration()

            if data.sensor_id in current_arm_config.sensors:
                if data.zone_number in current_arm_config.zones[data.sensor_id]:
                    return State.process_event(self, event, data)

            return StateType.armed

        else:
            return State.process_event(self, event, data)


class Alert(State):
    def __init__(self):
        State.__init__(self, StateType.alert)
        self.add_transition(EventType.disarm, StateType.disarmed)
        self.add_transition(EventType.alert_expired, StateType.alarm)

        self._transition_timer = None

    def on_entry(self):
        sensors.tone_generator.play_constant_tone()

        self._transition_timer = threading.Timer(alert_timeout_s, self.process_expired_alert)
        self._transition_timer.start()
        State.on_entry(self)

    def on_exit(self):
        sensors.tone_generator.stop_constant_tone()

        self._transition_timer.cancel()
        State.on_exit(self)

    def process_expired_alert(self):
        logger.info("Alert timer expired, transitioning to Alarm")
        alarm_state_machine.process_event(EventType.alert_expired, None)


class Alarm(State):
    def __init__(self):
        State.__init__(self, StateType.alarm)
        self.add_transition(EventType.disarm, StateType.disarmed)

    def on_entry(self):
        # turn on siren
        State.on_entry(self)

    def on_exit(self):
        # turn off siren
        State.on_exit(self)


class AlarmStateMachine:
    def __init__(self):
        self._state_machine = {StateType.disarmed: Disarmed(),
                               StateType.armed: Armed(),
                               StateType.alert: Alert(),
                               StateType.alarm: Alarm()}

        self._current_state = StateType.disarmed
        self._state_machine[self._current_state].on_entry()

    def get_current_state(self):
        return self._current_state

    def process_event(self, event, data):
        new_state = self._state_machine[self._current_state].process_event(event, data)

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


alarm_state_machine = AlarmStateMachine()
arm_configurations = ArmConfigurations()
alert_timeout_s = 30
