
import konnected
import collections
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
                self.load_output_pin((pin_number, pin_str), config)
            else:
                new_pin = Pin(pin_number)

                pin_zone = config[self.id].getint(pin_str + '_zone')
                if pin_zone is not None:
                    new_pin.zone = self.zones[pin_zone]
                    new_pin.zone.pins[pin_number] = new_pin

                self.pins[pin_number] = new_pin

    def load_output_pin(self, pin_params, config):
        pin_number, id_str = pin_params
        pin_name = config[self.id].get(id_str + '_name')

        if pin_name.lower() == 'chime':
            if tone_generator.pin_number != 0:
                logger.error('Duplicate chimes found.  Second Chime is pin ' + id_str + '. This will be ignored')

            tone_generator.pin_number = pin_number
            tone_generator.sensor = self
            tone_generator.load_chime_parameters_from_config(config['door_chime'])

        elif pin_name.lower() == 'siren':
            if siren.pin_number != 0:
                logger.error('Duplicate sirens found.  Second Chime is pin ' + id_str + '. This will be ignored')

            siren.pin_number = pin_number
            siren.sensor = self


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

    def process_door_chime(self):
        if self.chime_enabled:
            tone_generator.play_chime()


class Pin:
    def __init__(self, number):
        self.pin_number = number
        self.state = 0
        self.zone = None

    def update_state(self, new_state):
        self.state = new_state
        if self.zone is not None:
            self.zone.update_state()

    def get_zone_number(self):
        if self.zone is None:
            return 0
        return self.zone.number


class ToneGenerator:
    def __init__(self):
        self.pin_number = 0
        self.sensor = None

        self.number_of_beeps = 0
        self.beep_duration_ms = 0
        self.pause_duration_ms = 0

    def load_chime_parameters_from_config(self, config):
        self.number_of_beeps = config.getint('num_beeps')
        self.beep_duration_ms = config.getint('beep_duration_ms')
        self.pause_duration_ms = config.getint('pause_duration_ms')

    def play_constant_tone(self):
        logger.info("Playing tone")
        # self.sensor.konnected_client.put_device(self.pin_number, 1)

    def stop_constant_tone(self):
        logger.info("Stopping tone")
        # self.sensor.konnected_client.put_device(self.pin_number, 0)

    def play_chime(self):
        logger.info("Playing door chime")
        # self.sensor.konnected_client.put_device(self.pin_number,
        #                                         1,
        #                                         self.beep_duration_ms,
        #                                         self.number_of_beeps,
        #                                         self.pause_duration_ms)


class Siren:
    def __init__(self):
        self.pin_number = 0
        self.sensor = None

    def activate_siren(self):
        logger.info("Siren activated")
        # self.sensor.konnected_client.put_device(self.pin_number, 1)

    def deactivate_siren(self):
        logger.info("Siren deactivated")
        # self.sensor.konnected_client.put_device(self.pin_number, 0)


sensor_list = {}
tone_generator = ToneGenerator()
siren = Siren()
ZoneData = collections.namedtuple('ZoneData', ['sensor_id', 'zone_number'])


