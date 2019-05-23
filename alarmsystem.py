# Install the following packages with pip to use this script:
#   - requests (konnected needs this)
#   - flask
#   - flask-restful


from flask import Flask
from flask_restful import Api
import sys
import configparser
import logging
import panelhandler
import sensors

logging.basicConfig(level=logging.INFO)


def load_config(filename):
    config = configparser.ConfigParser()
    config.read(filename)

    sensors.load_sensors(config)


if __name__ == '__main__':

    config_filename = 'config.ini'
    if len(sys.argv) > 1:
        config_filename = sys.argv[1]
    logging.info("Using %s as the configuration file", config_filename)

    load_config(config_filename)

    app = Flask(__name__)
    api = Api(app)

    api.add_resource(panelhandler.PanelHandler, '/state')
    api.add_resource(sensors.SensorsHandler, '/device/<sensor_id>')
    api.add_resource(panelhandler.SettingsHandler, '/configuration')

    app.run(host="0.0.0.0", debug=True)


