# Install the following packages with pip to use this script:
#   - requests (konnected needs this)
#   - flask
#   - flask-restful


import konnected
from flask import Flask
from flask_restful import Api

import panelserver

# class Zone:
#     def __init__(self):
#         self._zones = konnected.Client()


if __name__ == '__main__':
    app = Flask(__name__)
    api = Api(app)

    panel = panelserver.PanelServer()
    panel.map_uris(api)

    app.run(debug=True)


