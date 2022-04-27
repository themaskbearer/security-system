import pytest
from pytest import fixture
import configparser

import alarmstates as als
import sensors


@fixture(scope='module')
def config_file():
    config = configparser.ConfigParser()
    config.read('test_config.ini')
    return config


@fixture()
def alarmstates_mocks(mocker):
    mocker.patch('alarmstates.sensors.tone_generator')
    mocker.patch('alarmstates.sensors.siren')
    mocker.patch('alarmstates.sensors.sensor_list')
    mocker.patch('alarmstates.threading.Timer')


def test_load_config(config_file):
    als.load_state_configurations(config_file)

    assert als.alert_timeout_s == 30


def test_arm_config(config_file):
    stay_name = 'Stay'
    stay_config = als.ArmConfiguration(stay_name, config_file[stay_name])

    assert stay_config.name == stay_name
    assert stay_config.sensors == ['123456789012']
    assert stay_config.zones == {'123456789012': [2, 3, 4]}


def test_arm_configs(config_file):
    arm_configs = als.ArmConfigurations()
    arm_configs.load_from_config(config_file)

    assert len(arm_configs.configurations) == 2
    assert arm_configs.configurations['Stay'].name == 'Stay'
    assert arm_configs.configurations['Away'].name == 'Away'


def test_valid_configs(config_file):
    als.load_state_configurations(config_file)

    assert als.arm_configurations.is_valid_arm_config('Stay') is True
    assert als.arm_configurations.is_valid_arm_config('Away') is True

    # Test a value that doesn't exist
    assert als.arm_configurations.is_valid_arm_config('Night') is False


@pytest.mark.parametrize('state, event, data, end_state',
                         [(als.StateType.disarmed, als.EventType.arm, 'Stay', als.StateType.armed),
                          (als.StateType.disarmed, als.EventType.disarm, None, als.StateType.disarmed),
                          (als.StateType.disarmed, als.EventType.sensor_changed, sensors.ZoneData('123456789012', 2), als.StateType.disarmed),
                          (als.StateType.disarmed, als.EventType.alert_expired, None, als.StateType.disarmed),
                          (als.StateType.armed, als.EventType.arm, 'Stay', als.StateType.armed),
                          (als.StateType.armed, als.EventType.disarm, None, als.StateType.disarmed),
                          (als.StateType.armed, als.EventType.sensor_changed, sensors.ZoneData('123456789012', 2), als.StateType.alert),
                          (als.StateType.armed, als.EventType.alert_expired, None, als.StateType.armed),
                          (als.StateType.alert, als.EventType.arm, 'Stay', als.StateType.alert),
                          (als.StateType.alert, als.EventType.disarm, None, als.StateType.disarmed),
                          (als.StateType.alert, als.EventType.sensor_changed, sensors.ZoneData('123456789012', 2), als.StateType.alert),
                          (als.StateType.alert, als.EventType.alert_expired, None, als.StateType.alarm),
                          (als.StateType.alarm, als.EventType.arm, 'Stay', als.StateType.alarm),
                          (als.StateType.alarm, als.EventType.disarm, None, als.StateType.disarmed),
                          (als.StateType.alarm, als.EventType.sensor_changed, sensors.ZoneData('123456789012', 2), als.StateType.alarm),
                          (als.StateType.alarm, als.EventType.alert_expired, None, als.StateType.alarm)
                          ])
def test_state_transitions(config_file, alarmstates_mocks, state, event, data, end_state):
    als.load_state_configurations(config_file)
    state_machine = als.AlarmStateMachine()

    # Shortcut to alert state
    state_machine._current_state = state
    state_machine._state_machine[state_machine._current_state].on_entry()

    # Process event
    state_machine.process_event(event, data)

    # Verify state
    assert state_machine.get_current_state() == end_state



