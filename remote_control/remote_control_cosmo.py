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
from rsd import RobotStateDisplay
import index_page
import cozmohelper

DEBUG_ANNOTATIONS_DISABLED = 0
DEBUG_ANNOTATIONS_ENABLED_VISION = 1
DEBUG_ANNOTATIONS_ENABLED_ALL = 2

flask_app = Flask(__name__)
remote_control_cozmo = None
cozmo_helper = None
_default_camera_image = flask_helpers.create_default_image(320, 240)
_is_mouse_look_enabled_by_default = False
_is_device_gyro_mode_enabled_by_default = False
_gyro_driving_deadzone_ratio = 0.025

_display_debug_annotations = DEBUG_ANNOTATIONS_ENABLED_ALL

@flask_app.route("/")
def handle_index_page():
    return index_page.html

def streaming_video(url_root):
    '''Video streaming generator function'''
    try:
        while True:
            if remote_control_cozmo:
                image = flask_helpers.get_annotated_image(remote_control_cozmo)

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

def is_microsoft_browser(request):
    agent = request.user_agent.string
    return 'Edge/' in agent or 'MSIE ' in agent or 'Trident/' in agent

@flask_app.route("/cozmoImage")
def handle_cozmoImage():
    if is_microsoft_browser(request):
        return flask_helpers.serve_single_image(remote_control_cozmo)
    return flask_helpers.stream_video(streaming_video, request.url_root)

def handle_key_event(key_request, is_key_down):
    message = json.loads(key_request.data.decode("utf-8"))
    if remote_control_cozmo:
        remote_control_cozmo.handle_key(key_code=(message['keyCode']), is_shift_down=message['hasShift'],
                                        is_ctrl_down=message['hasCtrl'], is_alt_down=message['hasAlt'],
                                        is_key_down=is_key_down)
    return ""

@flask_app.route('/shutdown', methods=['POST'])
def shutdown():
    flask_helpers.shutdown_flask(request)
    return ""

@flask_app.route('/keydown', methods=['POST'])
def handle_keydown():
    '''Called from Javascript whenever a key is down (note: can generate repeat calls if held down)'''
    return handle_key_event(request, is_key_down=True)

@flask_app.route('/keyup', methods=['POST'])
def handle_keyup():
    '''Called from Javascript whenever a key is released'''
    return handle_key_event(request, is_key_down=False)

@flask_app.route('/updateCozmo', methods=['POST'])
def handle_updateCozmo():
    return cozmo_helper.updateCozmo()

@flask_app.route('/user_cooperates', methods=['POST'])
def handle_button1():
    # user cooperated
    text = ""
    if remote_control_cozmo.cooperate:
        text = "(Cozmo is cooperating) User cooperated"
        # play successful response
        # TODO for now:
        remote_control_cozmo.say_text("yay let's blow it up")
        text = text + ''', Cozmo cooperated '''
    else:
        text = "(Cozmo is mirroring) User cooperated"
        # check what the user did the last time
        if remote_control_cozmo.user_cooperated_last_time:
            remote_control_cozmo.say_text("yay let's blow it up")
            text = text + ''', Cozmo cooperated '''
        else:
            remote_control_cozmo.say_text("I won't use mine! Use your own explosives and remove the obstacle yourself")
            text =  text + ''', Cozmo betrayed '''
        # if cozmo betrayed user, play appropriate animation
    # log cooperation
    remote_control_cozmo.user_cooperated_last_time = True
    return text

@flask_app.route('/user_betrays', methods=['POST'])
def handle_button2():
    # user betrayed cozmo, log betrayal
    # remote_control_cozmo.say_text("you betray")
    text = ""
    if remote_control_cozmo.cooperate:
        # remote_control_cozmo.say_text("i cooperate")
        # play betrayed response
        remote_control_cozmo.say_text("oh no. I will use my own explosives then")
        text = '''(Cozmo is cooperating) User betrayed, Cozmo cooperated '''
    else:
        text = '''(Cozmo is mirroring)'''
        # remote_control_cozmo.say_text("i mirror")
        # check what the user did the last time
        if remote_control_cozmo.user_cooperated_last_time:
            # remote_control_cozmo.say_text("i cooperate")
            remote_control_cozmo.say_text("oh no. I will use my own explosives then")
            text = text + '''User betrayed, Cozmo cooperated '''
        else:
            # remote_control_cozmo.say_text("i betray")
            remote_control_cozmo.say_text("okey let's walk then")
            text =  text + '''User betrayed, Cozmo betrayed '''
        # if cozmo betrayed user, play appropriate animation
    # log cooperation
    remote_control_cozmo.user_cooperated_last_time = False
    return text

@flask_app.route('/talk', methods=['POST'])
def handle_button3():
    remote_control_cozmo.say_text("Do you want to use your explosives?")
    return ""

@flask_app.route('/change_cooperation_setting', methods=['POST'])
def handle_button4():
    remote_control_cozmo.toggle_cooperation()
    return ""



def run(sdk_conn):
    robot = sdk_conn.wait_for_robot()
    robot.world.image_annotator.add_annotator('robotState', RobotStateDisplay)
    robot.enable_device_imu(True, True, True)

    global remote_control_cozmo
    remote_control_cozmo = RemoteControlCozmo(robot)
    global cozmo_helper
    cozmo_helper = cozmohelper.CozmoHelper(remote_control_cozmo)

    # Turn on image receiving by the camera
    robot.camera.image_stream_enabled = True

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

