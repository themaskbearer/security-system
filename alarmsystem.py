# Install the following packages with pip to use this script:
#   - requests (konnected needs this)
#   - flask
#   - flask-restful


from flask import Flask
from flask_restful import Api
import configparser
import logging
import argparse

import panelhandler
import alarmstates
import sensors
import konnected_server

logging.basicConfig(level=logging.INFO)


class AlarmSystem:
    def __init__(self, config_file='config.ini'):
        config = configparser.ConfigParser()
        config.read(config_file)

        sensors.load_sensors(config)
        alarmstates.load_state_configurations(config)


app = Flask(__name__)
api = Api(app)

api.add_resource(panelhandler.PanelHandler, '/state')
api.add_resource(konnected_server.SensorsHandler, '/device/<sensor_id>')
api.add_resource(panelhandler.SettingsHandler, '/configuration')

config_filename = 'config.ini'

parser = argparse.ArgumentParser()
parser.add_argument('--config')
args, extra_args = parser.parse_known_args()

if args.config:
    config_filename = args.config
logging.info("Using %s as the configuration file", config_filename)

alarm_system = AlarmSystem(config_filename)

if __name__ == '__main__':
    logging.info("Running standalone server")
    app.run(host="0.0.0.0", debug=True)


