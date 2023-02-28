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

import sys
import cozmo

try:
    from PIL import Image, ImageDraw
except ImportError:
    sys.exit("Cannot import from PIL: Do `pip3 install --user Pillow` to install")

# Annotator for displaying RobotState (position, etc.) on top of the camera feed
class RobotStateDisplay(cozmo.annotate.Annotator):
    def apply(self, image, scale):
        d = ImageDraw.Draw(image)

        bounds = [3, 0, image.width, image.height]

        def print_line(text_line):
            text = cozmo.annotate.ImageText(text_line, position=cozmo.annotate.TOP_LEFT, outline_color='black', color='lightblue')
            text.render(d, bounds)
            TEXT_HEIGHT = 11
            bounds[1] += TEXT_HEIGHT

        robot = self.world.robot  # type: cozmo.robot.Robot

        # Display the Pose info for the robot

        pose = robot.pose
        print_line('Pose: Pos = <%.1f, %.1f, %.1f>' % pose.position.x_y_z)
        print_line('Pose: Rot quat = <%.1f, %.1f, %.1f, %.1f>' % pose.rotation.q0_q1_q2_q3)
        print_line('Pose: angle_z = %.1f' % pose.rotation.angle_z.degrees)
        print_line('Pose: origin_id: %s' % pose.origin_id)

        # Display the Accelerometer and Gyro data for the robot

        print_line('Accelmtr: <%.1f, %.1f, %.1f>' % robot.accelerometer.x_y_z)
        print_line('Gyro: <%.1f, %.1f, %.1f>' % robot.gyro.x_y_z)

        # Display the Accelerometer and Gyro data for the mobile device

        if robot.device_accel_raw is not None:
            print_line('Device Acc Raw: <%.2f, %.2f, %.2f>' % robot.device_accel_raw.x_y_z)
        if robot.device_accel_user is not None:
            print_line('Device Acc User: <%.2f, %.2f, %.2f>' % robot.device_accel_user.x_y_z)
        if robot.device_gyro is not None:
            mat = robot.device_gyro.to_matrix()
            print_line('Device Gyro Up: <%.2f, %.2f, %.2f>' % mat.up_xyz)
            print_line('Device Gyro Fwd: <%.2f, %.2f, %.2f>' % mat.forward_xyz)
            print_line('Device Gyro Left: <%.2f, %.2f, %.2f>' % mat.left_xyz)