from flask import Flask
from flask_cors import CORS

from src.utils.config import Config
import src.utils.constants as consts
from flasgger import Swagger
from src.server.views.view import view as email_view

app = Flask(__name__)
CORS(app)
swagger = Swagger(app)


class RunServer:
    def __init__(self, section: str):
        self.server_port = Config().get(section=section, param=consts.CONFIG_PORT_TOKEN)
        url_prefix = Config().get(section=section,
                                  param=consts.CONFIG_URL_PREFIX_TOKEN,
                                  default_value=consts.DEFAULT_URL_PREFIX)
        app.register_blueprint(email_view, url_prefix=url_prefix)

    def run_server(self):
        app.run(host='0.0.0.0', port=self.server_port, use_debugger=False,
                use_reloader=False, passthrough_errors=True)
