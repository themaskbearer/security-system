import pytest
from pytest import fixture
import configparser

import sensors


@fixture(scope='module')
def config_file():
    config = configparser.ConfigParser()
    config.read('test_config.ini')
    return config


@fixture()
def sensor_mocks(mocker):
    mocker.patch('sensors.konnected.Client')
    mocker.patch('sensors.SensorLivenessCheck')


@fixture()
def test_sensor(sensor_mocks, config_file):
    return sensors.Sensor(config_file['123456789012'])


def test_load_sensors(sensor_mocks, config_file):
    sensors.load_sensors(config_file)

    assert len(sensors.sensor_list) == 1


def test_sensor_init(test_sensor):
    assert test_sensor.id == '123456789012'
    assert test_sensor.ip == '192.168.1.123'
    assert test_sensor.port == '12345'

    assert test_sensor.total_pins == 8
    assert test_sensor.total_zones == 3


def test_sensor_load_zones_and_pins(test_sensor, config_file):
    test_sensor.load_zones_and_pins(config_file)

    # Verify zone/pin totals are correct
    assert len(test_sensor.zones) == 3
    assert len(test_sensor.input_pins) == 6
    assert len(test_sensor.output_pins) == 2

    # Verify Zone creation
    # Verify Zone 1 properties
    assert test_sensor.zones[1].number == 1
    assert test_sensor.zones[1].name == 'Front Door'
    assert test_sensor.zones[1].chime_enabled is True
    # Verify Zone 1 pins are correctly linked
    assert len(test_sensor.zones[1].pins) == 1
    assert test_sensor.zones[1].pins[2] is test_sensor.input_pins[2]

    # Verify Zone 2 properties
    assert test_sensor.zones[2].number == 2
    assert test_sensor.zones[2].name == 'Back Door'
    assert test_sensor.zones[2].chime_enabled is False
    # Verify Zone 2 pins are correctly linked
    assert len(test_sensor.zones[2].pins) == 2
    assert test_sensor.zones[2].pins[3] is test_sensor.input_pins[3]
    assert test_sensor.zones[2].pins[4] is test_sensor.input_pins[4]

    # Verify Zone 3 properties
    assert test_sensor.zones[3].number == 3
    assert test_sensor.zones[3].name == ''
    assert test_sensor.zones[3].chime_enabled is False
    # Verify Zone 3 pins are correctly linked
    assert len(test_sensor.zones[3].pins) == 0

    # Verify Input Pin Creation
    # Verify Pin 2 properties
    assert test_sensor.input_pins[2].pin_number == 2
    assert test_sensor.input_pins[2].zone is test_sensor.zones[1]

    # Verify Pin 3 properties
    assert test_sensor.input_pins[3].pin_number == 3
    assert test_sensor.input_pins[3].zone is test_sensor.zones[2]

    # Verify Pin 4 properties
    assert test_sensor.input_pins[4].pin_number == 4
    assert test_sensor.input_pins[4].zone is test_sensor.zones[2]

    # Verify Pin 5-7 properties
    for pin in range(5, 7):
        assert test_sensor.input_pins[pin].pin_number == pin
        assert test_sensor.input_pins[pin].zone is None

    # Verify Output Pin creation
    # Verify chime
    assert test_sensor.output_pins[1].pin_number == 1
    assert test_sensor.output_pins[1].zone is None

    assert sensors.tone_generator.pin_number == 1
    assert sensors.tone_generator.sensor is test_sensor

    # Verify alarm
    assert test_sensor.output_pins[8].pin_number == 8
    assert test_sensor.output_pins[8].zone is None

    assert sensors.siren.pin_number == 8
    assert sensors.siren.sensor is test_sensor


@pytest.mark.parametrize('pins, result',
                         [([{'pin': 1}, {'pin': 8}], True),
                          ([{'pin': 1}], False),
                          ([{'pin': 1}, {'pin': 8}, {'pin': 3}], False),
                          ([{'pin': 1}, {'pin': 3}], False)
                          ])
def test_sensor_liveness_check_compare_pins(pins, result):
    correct_pins = {1: sensors.Pin(1), 8: sensors.Pin(8)}

    assert sensors.SensorLivenessCheck.compare_pins(correct_pins, pins) is result


def test_pin_zone_update(test_sensor, config_file):
    test_sensor.load_zones_and_pins(config_file)

    pin3 = test_sensor.input_pins[3]
    pin4 = test_sensor.input_pins[4]

    test_zone = test_sensor.zones[2]

    # Ensure zone starts at 0
    assert test_zone.state == 0

    # Update pin 2 and verify zone updates
    pin3.update_state(1)
    assert test_zone.state == 1

    # Update pin 3 and verify zone is still 1
    pin4.update_state(1)
    assert test_zone.state == 1

    # Clear pin 2 and verify zone is still 1
    pin3.update_state(0)
    assert test_zone.state == 1

    # Clear pin 3 and verify zone clears
    pin4.update_state(0)
    assert test_zone.state == 0


def test_tone_generator_config(config_file):
    chime = sensors.ToneGenerator()
    chime.load_chime_parameters_from_config(config_file['door_chime'])

    assert chime.number_of_beeps == 3
    assert chime.beep_duration_ms == 200
    assert chime.pause_duration_ms == 50
