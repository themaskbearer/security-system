# Install the following packages with pip to use this script:
#   - requests (konnected needs this)
#   - flask
#   - flask-restful

from enum import Enum
import konnected
from flask import Flask
from flask_restful import Resource, Api, reqparse


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

    def get_zone_status(self):
        pass

    def process_command(self, command):
        pass


# class Zone:
#     def __init__(self):
#         self._zones = konnected.Client()

list_of_states = {StateType.disarmed: Disarmed(), StateType.armed: Armed(), StateType.warning: Warning(),
                  StateType.alarm: Alarm()}

state = list_of_states[StateType.disarmed].process_event(EventType.arm)
state = list_of_states[state].process_event(EventType.disarm)
state = list_of_states[state].process_event(EventType.arm)
state = list_of_states[state].process_event(EventType.sensor_tripped)

print(state)

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument("event")


class SystemState(Resource):
    def get(self):
        return {'current state': state.name}

    def put(self):
        global state
        args = parser.parse_args()
        event = EventType[args['event']]
        state = list_of_states[state].process_event(event)
        return {'current state': state.name}, 201


api.add_resource(SystemState, '/state')

if __name__ == '__main__':
    app.run(debug=True)


