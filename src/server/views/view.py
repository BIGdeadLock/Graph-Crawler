
import asyncio

from flasgger import swag_from
from flask import Blueprint, request, jsonify
from flask_cors import CORS
import logging as log
from src.server.server import ServerInterface
import src.utils.constants as consts
import src.server.views.uri as uri

view = Blueprint("email", __name__)
CORS(view)


@view.route(uri.BUILD_GRAPH, methods=[consts.POST_TOKEN])
# @swag_from(f'{os.path.join(consts.SCHEMAS_DIR_PATH, consts.PLAYBOOK_YML_FILE_NAME)}')
def get_playbook():
    try:
        content = request.json
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        ret = loop.run_until_complete(ServerInterface().build_graph(content))
        resp = jsonify(ret)
        resp.status_code = consts.HTTP_OK
    except Exception as e:
        err = f"{e}"
        log.error(f"Error: {err}")
        resp = jsonify({"Error": err})
        resp.status_code = consts.RESP_SERVER_ERROR_VAL
        log.info(f"response {resp}")

    return resp
