#  P2PFaaS - A framework for FaaS Load Balancing
#  Copyright (c) 2019 - 2022. Gabriele Proietti Mattia <pm.gabriele@outlook.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

import asyncio
import json
from threading import Thread

from flask import Flask, request
from waitress import serve
from websockets import serve as ws_serve

import api.learn
import learners
import log
from api.utils import Utils
from config import ConfigurationStatic, ConfigurationDynamic
from learners.learner import Learner
from log import Log
from models import ActEntry

_MODULE_NAME = "Main"

# start server
app = Flask(__name__)


#
# Webserver
#

@app.route('/')
def hello():
    return f"This is {configurationStatic.get_app_name()} v{configurationStatic.get_app_version()}."


@app.route('/act', methods=['GET'])
def act():
    # pass only the state
    success, act_output = api.learn.Learn.act(request)

    if not success:
        res = Utils.prepare_res(500)
        return res

    headers = {Utils.HEADER_EPSILON: act_output.eps}
    res = Utils.prepare_res(200, headers=headers, content_str=f"{act_output.action}")

    return res


@app.route('/train', methods=['GET'])
def train():
    success = api.learn.Learn.train(request)
    if not success:
        res = Utils.prepare_res(500)
        return res

    return "ok"


@app.route('/train_batch', methods=['POST'])
def train_batch():
    success = api.learn.Learn.train_batch(request)
    if not success:
        res = Utils.prepare_res(500)
        return res

    return "ok"


@app.route('/learner/parameters', methods=['GET'])
def learner_parameters():
    """Returns the current learner description"""
    Log.mdebug(_MODULE_NAME, f"learner_parameters: called")
    res = {
        "name": configurationDynamic.get_learner_name(),
        "parameters": configurationDynamic.get_learner_parameters()
    }
    return Utils.prepare_res_json(res)


@app.route('/learner/parameters', methods=['POST'])
def learner_parameters_post():
    """Returns the current learner description"""
    Log.mdebug(_MODULE_NAME, f"learner_parameters_post: called")

    # retrieve the passed parameters
    res = learner.set_parameters(request.get_json())

    if res:
        # if saved correctly then save the parameters to a file
        configurationDynamic.set_learner_name(learner.get_name())
        configurationDynamic.set_learner_parameters(learner.get_parameters())

    Log.mdebug(_MODULE_NAME, f"learner_parameters_post: result={res}")
    return Utils.prepare_res(200 if res else 500)


@app.route('/learner/stats')
def learner_stats():
    """Returns the current learner description"""
    return Utils.prepare_res_json(learner.get_stats())


@app.route('/learner/weights', methods=['GET'])
def learner_weights():
    """Returns the current learner description"""
    return Utils.prepare_res_json(learner.get_weights())


@app.route('/learner/reset')
def reset():
    """Reset the weights learned"""
    learner.reset()
    return ""


#
# Socket
#

async def ws_act(websocket):
    try:
        async for message in websocket:
            state_usable = json.loads(message)
            Log.mdebug(_MODULE_NAME, f"websocket={websocket}, message={message.strip()}, parsed={state_usable}")

            # prepare the act
            learner = learners.learner.Learner.instance()

            act_entry = ActEntry()
            act_entry.state = state_usable

            result = learner.act(act_entry)

            await websocket.send(f"{result.action:.5f},{result.eps:.5f}")
    except Exception as e:
        log.Log.mwarn(_MODULE_NAME, f"ws_act: socket error: {e}")


async def ws_main(port):
    async with ws_serve(ws_act, "0.0.0.0", port):
        await asyncio.Future()  # run forever


def ws_init():
    asyncio.run(ws_main(8765))


#
# Entrypoint
#

configurationStatic = ConfigurationStatic.instance()
configurationDynamic = ConfigurationDynamic.instance()

if __name__ == '__main__':
    Log.minfo(_MODULE_NAME,
              f"Starting {configurationStatic.get_app_name()} v{configurationStatic.get_app_version()}")
    Log.minfo(_MODULE_NAME,
              f"Started listening at {configurationStatic.get_listening_host()}:{configurationStatic.get_listening_port()}")

    # init learner, refresh the parameters
    learner = Learner.instance()
    learner.set_learner(configurationDynamic.get_learner_name(), configurationDynamic.get_learner_parameters())
    learner.start()
    configurationDynamic.set_learner_parameters(learner.get_parameters())
    configurationDynamic.set_learner_name(learner.get_name())

    # start socket server
    Log.minfo(_MODULE_NAME, "Starting socket listening")
    # asyncio.run(ws_main(8765))
    Thread(target=ws_init).start()

    # start webserver
    Log.minfo(_MODULE_NAME, "Starting webserver")
    serve(app, host=configurationStatic.get_listening_host(), port=configurationStatic.get_listening_port())

    # http_server = WSGIServer((
    #    configurationStatic.get_listening_host(),
    #     configurationStatic.get_listening_port()),
    #     app,
    #     log=None)
    # http_server.serve_forever()
