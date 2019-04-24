
from flask_restful import Resource, reqparse
import alarmstates

parser = reqparse.RequestParser()
parser.add_argument("event")

alarm_state_machine = alarmstates.AlarmStateMachine()


class SystemState(Resource):
    def get(self):
        # TODO: need to differentiate between state requests and sensor requests, or just include everything
        return {'current state': alarm_state_machine.get_current_state().name}

    def post(self):
        args = parser.parse_args()
        event = alarmstates.EventType[args['event']]
        if not alarmstates.AlarmStateMachine.is_valid_external_event(event):
            return {'error': 'invalid event ' + args['event']}, 400

        state = alarm_state_machine.process_event(event)
        return {'current state': state.name}, 201

    def put(self):
        # This will be used for configuration updates
        pass

    def map_uris(self, api):
        api.add_resource(SystemState, '/state')

