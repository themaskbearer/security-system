

from flask import request
from flask_restful import Resource, reqparse, abort
import json
import logging

import alarmstates
import sensors

logger = logging.getLogger(__name__)

put_parser = reqparse.RequestParser()
put_parser.add_argument('state')
put_parser.add_argument('pin')

get_parser = reqparse.RequestParser()
get_parser.add_argument('pin', type=int)


def abort_if_doesnt_exist(sensor_id):
    if sensor_id not in sensors.sensor_list:
        logger.info("Failed to find sensor id " + str(sensor_id) + " in available sensors")
        abort(404, message="Sensor ID {} doesn't exist".format(sensor_id))


class SensorsHandler(Resource):
    def get(self, sensor_id):
        # This call is primarily used on startup to query what the state of the output pins should be
        logger.info("GET function for sensor_id " + str(sensor_id) + ", raw data: " + request.get_data(as_text=True))
        abort_if_doesnt_exist(sensor_id)
        args = get_parser.parse_args()

        # TODO: get initial state from config file
        return {'state': 0, 'pin': args['pin']}

    def put(self, sensor_id):
        logger.info("PUT function for sensor_id " + str(sensor_id) + ", raw data: " + request.get_data(as_text=True))
        abort_if_doesnt_exist(sensor_id)

        args = put_parser.parse_args()
        pin_number = int(args['pin'])
        if pin_number not in sensors.sensor_list[sensor_id].pins:
            abort(404, message="Pin number {} not found in sensor {}".format(args['pin'], sensor_id))

        pin = sensors.sensor_list[sensor_id].pins[pin_number]
        pin.update_state(int(args['state']))

        zone_data = sensors.ZoneData(sensor_id, pin.zone.number)
        alarmstates.alarm_state_machine.process_event(alarmstates.EventType.sensor_changed, zone_data)

        return 200
