import pytest
from pytest import fixture
import configparser

import alarmstates


@fixture(scope='module')
def config_file():
    config = configparser.ConfigParser()
    config.read('test_config.ini')
    return config


@fixture()
def alarmstates_mocks(mocker):
    mocker.patch('alarmstates.sensors.tone_generator')
    mocker.patch('alarmstates.threading.Timer')


def test_load_config(config_file):
    alarmstates.load_state_configurations(config_file)

    assert alarmstates.alert_timeout_s == 30


def test_arm_config(config_file):
    stay_name = 'Stay'
    stay_config = alarmstates.ArmConfiguration(stay_name, config_file[stay_name])

    assert stay_config.name == stay_name
    assert stay_config.sensors == ['123456789012']
    assert stay_config.zones == {'123456789012': [2, 3, 4]}


def test_arm_configs(config_file):
    arm_configs = alarmstates.ArmConfigurations()
    arm_configs.load_from_config(config_file)

    assert len(arm_configs.configurations) == 2
    assert arm_configs.configurations['Stay'].name == 'Stay'
    assert arm_configs.configurations['Away'].name == 'Away'


def test_valid_configs(config_file):
    alarmstates.load_state_configurations(config_file)

    assert alarmstates.is_valid_arm_config('Stay') is True
    assert alarmstates.is_valid_arm_config('Away') is True

    # Test a value that doesn't exist
    assert alarmstates.is_valid_arm_config('Night') is False


def test_alert_transition(config_file, alarmstates_mocks):
    alarmstates.load_state_configurations(config_file)
    alert_state = alarmstates.Alert()
    alert_state.on_entry()
    alert_state.process_expired_alert()

    assert alarmstates.alarm_state_machine.get_current_state() == alarmstates.StateType.alarm