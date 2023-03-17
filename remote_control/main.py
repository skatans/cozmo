#!/usr/bin/env python3

# Copyright (c) 2016 Anki, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the file LICENSE.txt or at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Modifications by Tuisku Polvinen and Adam Bengtsson 2023

'''Control Cozmo using a webpage on your computer.
This example lets you control Cozmo by Remote Control, using a webpage served by Flask.
'''

import asyncio
import io
import json
import math
import sys

sys.path.append('../lib/')
import flask_helpers
import cozmo

# check that the required packages are installed
try:
    from flask import Flask, request
except ImportError:
    sys.exit("Cannot import from flask: Do `pip3 install --user flask` to install")
try:
    from PIL import Image, ImageDraw
except ImportError:
    sys.exit("Cannot import from PIL: Do `pip3 install --user Pillow` to install")
try:
    import requests
except ImportError:
    sys.exit("Cannot import from requests: Do `pip3 install --user requests` to install")

from remote_cozmo import RemoteControlCozmo
import index_page

flask_app = Flask(__name__)
rc_cozmo = None

@flask_app.route("/")
def handle_index_page():
    return index_page.html

def streaming_video(url_root):
    '''Video streaming generator function'''
    try:
        while True:
            if rc_cozmo:
                image = flask_helpers.get_annotated_image(rc_cozmo)

                img_io = io.BytesIO()
                image.save(img_io, 'PNG')
                img_io.seek(0)
                yield (b'--frame\r\n'
                    b'Content-Type: image/png\r\n\r\n' + img_io.getvalue() + b'\r\n')
            else:
                asyncio.sleep(.1)
    except cozmo.exceptions.SDKShutdown:
        # Tell the main flask thread to shutdown
        requests.post(url_root + 'shutdown')

@flask_app.route("/cozmoImage")
def handle_cozmoImage():
    #Check if the browser is MS Edge for compability tweaks
    agent = request.user_agent.string
    if 'Edge/' in agent or 'MSIE ' in agent or 'Trident/' in agent:
        return flask_helpers.serve_single_image(rc_cozmo)
    #otherwise stream normally
    return flask_helpers.stream_video(streaming_video, request.url_root)

def handle_key_event(key_request, is_key_down):
    # parse keyboard events
    message = json.loads(key_request.data.decode("utf-8"))
    if rc_cozmo:
        rc_cozmo.handle_key(key_code=(message['keyCode']), is_shift_down=message['hasShift'],
                                        is_ctrl_down=message['hasCtrl'], is_alt_down=message['hasAlt'],
                                        is_key_down=is_key_down)
    return ""

@flask_app.route('/shutdown', methods=['POST'])
def shutdown():
    flask_helpers.shutdown_flask(request)
    return ""

@flask_app.route('/keydown', methods=['POST'])
def handle_keydown():
    #Called from Javascript whenever a key is down (note: can generate repeat calls if held down)
    return handle_key_event(request, is_key_down=True)

@flask_app.route('/keyup', methods=['POST'])
def handle_keyup():
    #Called from Javascript whenever a key is released
    return handle_key_event(request, is_key_down=False)

@flask_app.route('/updateCozmo', methods=['POST'])
def handle_updateCozmo():
    rc_cozmo.update()
    return ""

def handle_user_choice(user_cooperated_now):
    rc_cozmo.user_is_cooperating = user_cooperated_now
    cozmo_reaction = ""

    # cozmo cooperates or user cooperated last time
    if rc_cozmo.cooperate or rc_cozmo.user_cooperated_last_time:
        if user_cooperated_now:
            # play successful response
            rc_cozmo.say_text(rc_cozmo.response_cooperation)
        else:
            rc_cozmo.say_text(rc_cozmo.response_is_betrayed)
        cozmo_reaction = ''', Cozmo cooperated '''
    
    # cozmo mirrors and user did not cooperate last time
    else:
        if user_cooperated_now:
            rc_cozmo.say_text(rc_cozmo.response_betray_user)
        else:
            # punishment for mutual betrayal
            rc_cozmo.say_text(rc_cozmo.response_both_betray)
        cozmo_reaction =  ''', Cozmo betrayed '''
    # save user choice
    rc_cozmo.user_cooperated_last_time = user_cooperated_now
    return rc_cozmo.get_log_text() + cozmo_reaction

@flask_app.route('/user_cooperates', methods=['POST'])
def handle_user_cooperation():
    # User cooperated
    return handle_user_choice(True)

@flask_app.route('/user_betrays', methods=['POST'])
def handle_user_betrayal():
    # user betrayed cozmo
    return handle_user_choice(False)

@flask_app.route('/talk', methods=['POST'])
def handle_talk():
    rc_cozmo.say_text("Do you want to use your explosives?")
    return ""

@flask_app.route('/change_cooperation_setting', methods=['POST'])
def handle_cooperation_setting_change():
    rc_cozmo.toggle_cooperation()
    return f"=== Cooperation setting changed to {'Cooperation' if rc_cozmo.cooperate else 'Mirroring'} and user action log reset ==="


def run(sdk_conn):
    robot = sdk_conn.wait_for_robot()
    robot.enable_device_imu(True, True, True)

    # set up the robot and helper class
    global rc_cozmo
    rc_cozmo = RemoteControlCozmo(robot)

    # Turn on image receiving by the camera
    robot.camera.image_stream_enabled = True

    # Run the Flask server
    flask_helpers.run_flask(flask_app)


if __name__ == '__main__':
    cozmo.setup_basic_logging()
    cozmo.robot.Robot.drive_off_charger_on_connect = False  # RC can drive off charger if required
    try:
        cozmo.connect(run)
    except KeyboardInterrupt as e:
        pass
    except cozmo.ConnectionError as e:
        sys.exit("A connection error occurred: %s" % e)

