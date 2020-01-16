
from flask import request
from flask_restful import Resource, reqparse, abort
import logging
import json

import alarmstates

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
        new_sensor.total_pins = config[sensor_id].getint('pins', 0)
        new_sensor.ip = config[sensor_id].get('ip', "127.0.0.1")
        new_sensor.port = config[sensor_id].get('port', 65000)

        new_sensor.total_zones = config[sensor_id].getint('zones', 0)

        for zone_number in range(1, new_sensor.total_zones + 1):
            new_zone = Zone()
            new_zone.number = zone_number
            new_zone.name = config[sensor_id].get('zone' + str(zone_number) + '_name', '')
            new_sensor.zones[zone_number] = new_zone

        for pin_number in range(1, new_sensor.total_pins + 1):
            pin_str = 'pin' + str(pin_number)

            pin_type = config[sensor_id].get(pin_str)
            if pin_type.lower() == 'output':
                # Do stuff for output pins
                pass
            else:
                new_pin = Pin()
                new_pin.pin = pin_number

                pin_zone = config[sensor_id].getint(pin_str + '_zone')
                if pin_zone is not None:
                    new_pin.zone = new_sensor.zones[pin_zone]
                    new_pin.zone.pins[pin_number] = new_pin

                new_sensor.pins[pin_number] = new_pin

        sensor_list[sensor_id] = new_sensor


class Sensor:
    def __init__(self):
        self.id = ""
        self.total_pins = 0
        self.total_zones = 0
        self.ip = "127.0.0.1"
        self.port = 12345

        self.zones = {}
        self.pins = {}


class Zone:
    def __init__(self):
        self.number = 0
        self.pins = {}
        self.state = 0
        self.name = ""

    def update_state(self):
        new_state = 0
        for pin in self.pins:
            new_state = new_state or self.pins[pin].state

        self.state = new_state


class Pin:
    def __init__(self):
        self.pin_number = 0
        self.state = 0
        self.zone = None


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
        pin_number = int(args['pin'])
        if pin_number not in sensor_list[sensor_id].pins:
            abort(404, message="Pin number {} not found in sensor {}".format(args['pin'], sensor_id))

        pin = sensor_list[sensor_id].pins[pin_number]
        pin.state = int(args['state'])

        # TODO: Process door chime

        if pin.zone is not None:
            pin.zone.update_state()

            if pin.zone.state == 1:
                zone_data = (sensor_id, pin.zone.number)
                alarmstates.alarm_state_machine.process_event(alarmstates.EventType.sensor_changed, zone_data)

        return 200

