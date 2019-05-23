
from flask_restful import Resource, reqparse
import configparser
import json
import alarmstates

parser = reqparse.RequestParser()
parser.add_argument("event")

alarm_state_machine = alarmstates.AlarmStateMachine()


class PanelHandler(Resource):
    def get(self):
        return {'current state': alarm_state_machine.get_current_state().name}

    def post(self):
        args = parser.parse_args()
        event = alarmstates.EventType[args['event']]
        # TODO: Re-enable this when testing is done
        # if not alarmstates.AlarmStateMachine.is_valid_external_event(event):
        #     return {'error': 'invalid event ' + args['event']}, 400

        state = alarm_state_machine.process_event(event)
        return {'current state': state.name}, 201


class SettingsHandler(Resource):
    def get(self):
        # TODO: clean this up to not reload config and display necessary info
        config = configparser.ConfigParser()
        config.read('config.ini')

        settings = {'door_chime': config.items('door_chime'),
                    'warning': config.items('warning')}

        return json.dumps(settings)

    def put(self):
        return 200
