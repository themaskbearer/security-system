
import konnected
import logging
logger = logging.getLogger(__name__)


def load_sensors(config):
    sensors_ids = config['sensors'].get('sensors')
    sensor_id_list = sensors_ids.split(',')

    for sensor_id in sensor_id_list:
        new_sensor = Sensor(config[sensor_id])
        new_sensor.load_zones_and_pins(config)

        sensor_list[sensor_id] = new_sensor


class Sensor:
    def __init__(self, config):
        self.id = config.name
        self.ip = config.get('ip', "127.0.0.1")
        self.port = config.get('port', 65000)

        self.total_pins = config.getint('pins', 0)
        self.total_zones = config.getint('zones', 0)

        self.konnected_client = konnected.Client(self.ip, self.port)

        self.zones = {}
        self.pins = {}

    def load_zones_and_pins(self, config):
        for zone_number in range(1, self.total_zones + 1):
            new_zone = Zone(zone_number, config[self.id])
            self.zones[zone_number] = new_zone

        for pin_number in range(1, self.total_pins + 1):
            pin_str = 'pin' + str(pin_number)

            pin_type = config[self.id].get(pin_str)
            if pin_type.lower() == 'output':
                pin_name = config[self.id].get(pin_str + '_name')

                if pin_name.lower() == 'chime':
                    if door_chime.pin_number != 0:
                        logger.error('Duplicate door chimes found.  Second Chime is pin ' + pin_str + '. This will be ignored')

                    door_chime.pin_number = pin_number
                    door_chime.sensor = self
                    door_chime.load_chime_parameters_from_config(config['door_chime'])

                elif pin_name.lower() == 'siren':
                    pass
            else:
                new_pin = Pin(pin_number)

                pin_zone = config[self.id].getint(pin_str + '_zone')
                if pin_zone is not None:
                    new_pin.zone = self.zones[pin_zone]
                    new_pin.zone.pins[pin_number] = new_pin

                self.pins[pin_number] = new_pin


class Zone:
    def __init__(self, number, config):
        self.number = number
        self.name = config.get('zone' + str(number) + '_name', '')
        self.chime_enabled = config.getboolean('zone' + str(number) + '_chime')

        self.pins = {}
        self.state = 0

    def update_state(self):
        new_state = 0
        for pin in self.pins:
            new_state = new_state or self.pins[pin].state

        self.state = new_state


class Pin:
    def __init__(self, number):
        self.pin_number = number
        self.state = 0
        self.zone = None


class DoorChime:
    def __init__(self):
        self.pin_number = 0
        self.sensor = None

        self.number_of_beeps = 0
        self.beep_duration_ms = 0
        self.pause_duration_ms = 0

    def load_chime_parameters_from_config(self, config):
        pass

    def play_chime(self):
        logger.info("Playing door chime")
        # self.sensor.konnected_client.put_device(self.pin_number,
        #                                         1,
        #                                         self.beep_duration_ms,
        #                                         self.number_of_beeps,
        #                                         self.pause_duration_ms)


class Siren:
    def __init(self):
        self.pin_number = 0
        self.sensor = None

    def activate_siren(self):
        pass

    def deactivate_siren(self):
        pass


sensor_list = {}
door_chime = DoorChime()
siren = Siren()



