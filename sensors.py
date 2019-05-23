
from flask import request
from flask_restful import Resource, reqparse, abort
import logging
import json

logger = logging.getLogger(__name__)


sensor_list = {}

parser = reqparse.RequestParser()
parser.add_argument('state')
parser.add_argument('pin')


def load_sensors(config):
    sensors_ids = config['sensors'].get('sensors')
    sensor_id_list = sensors_ids.split(',')

    for sensor_id in sensor_id_list:
        new_sensor = Sensor()
        new_sensor.id = sensor_id
        new_sensor.pins = config[sensor_id].getint('pins', 0)
        new_sensor.ip = config[sensor_id].get('ip', "127.0.0.1")
        new_sensor.port = config[sensor_id].get('port', 65000)

        for pin_number in range(1, new_sensor.pins + 1):
            pin_str = 'pin' + str(pin_number)

            pin_type = config[sensor_id].get(pin_str)
            if pin_type.lower() == 'output':
                # Do stuff for output pins
                pass
            else:
                new_zone = Zone()
                new_zone.name = config[sensor_id].get(pin_str + '_name', '')
                new_zone.sensor_id = sensor_id
                new_zone.pin = pin_number

                new_sensor.zones[pin_number] = new_zone

        sensor_list[sensor_id] = new_sensor


class Sensor:
    def __init__(self):
        self.id = ""
        self.pins = 0
        self.ip = "127.0.0.1"
        self.port = 12345

        self.zones = {}


class Zone:
    def __init__(self):
        self.sensor_id = ""
        self.pin = 0
        self.state = 0
        self.name = ""


class SensorsHandler(Resource):
    def abort_if_doesnt_exist(self, sensor_id):
        if sensor_id not in sensor_list:
            logger.info("Failed to find sensor id " + str(sensor_id) + " in available sensors")
            abort(404, message="Sensor ID {} doesn't exist".format(sensor_id))

    def get(self, sensor_id):
        logger.info("GET function for sensor_id " + str(sensor_id) + ", raw data: " + request.get_data(as_text=True))
        self.abort_if_doesnt_exist(sensor_id)

        # TODO: determine serialization to return
        # Does this matter?  This is for konnected
        return json.dumps(sensor_list[sensor_id], default=lambda o: o.__dict__, indent=4)

    def put(self, sensor_id):
        logger.info("PUT function for sensor_id " + str(sensor_id) + ", raw data: " + request.get_data(as_text=True))
        self.abort_if_doesnt_exist(sensor_id)

        args = parser.parse_args()
        pin = int(args['pin'])
        if pin not in sensor_list[sensor_id].zones:
            abort(404, message="Pin number {} not found in sensor {}".format(args['pin'], sensor_id))

        sensor_list[sensor_id].zones[pin].state = int(args['state'])

        return 200

