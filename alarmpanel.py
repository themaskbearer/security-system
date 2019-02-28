
from flask_restful import Resource, reqparse
import alarmstates

parser = reqparse.RequestParser()
parser.add_argument("event")

alarm_system = alarmstates.AlarmSystem()


class SystemState(Resource):
    def get(self):
        return {'current state': alarm_system.get_current_state().name}

    def put(self):
        args = parser.parse_args()
        event = alarmstates.EventType[args['event']]
        state = alarm_system.process_event(event)
        return {'current state': state.name}, 201

    def map_uris(self, api):
        api.add_resource(SystemState, '/state')

