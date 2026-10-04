#!/usr/bin/env python

# Copyright 2025 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time

from lerobot.robots.lekiwi import LeKiwiBaseClient, LeKiwiBaseClientConfig
from lerobot.teleoperators.keyboard.teleop_keyboard import KeyboardTeleop, KeyboardTeleopConfig
from lerobot.utils.robot_utils import precise_sleep
from lerobot.utils.visualization_utils import init_rerun, log_rerun_data

FPS = 30


def main():
    # Create the robot and teleoperator configurations
    # Note: Replace remote_ip with the actual IP of the robot
    robot_config = LeKiwiBaseClientConfig(remote_ip="192.168.1.192", id="my_lekiwi_base")
    keyboard_config = KeyboardTeleopConfig(id="my_laptop_keyboard")

    # Initialize the robot and teleoperator
    robot = LeKiwiBaseClient(robot_config)
    keyboard = KeyboardTeleop(keyboard_config)

    # Connect to the robot and teleoperator
    # On the LeKiwi, start the host first:
    # `python -m lerobot.robots.lekiwi.lekiwi_host --robot.type=lekiwi_base --robot.id=my_lekiwi_base`
    #
    # Troubleshooting "Timeout waiting for LeKiwi Host to connect expired":
    # The client needs the host's ZMQ ports reachable: 5555 (commands) and 5556 (observations).
    # If the host is running (on the robot: `ss -tlnp | grep -E '5555|5556'` shows LISTEN) and the
    # robot pings, but the client still times out, a firewall on the robot is likely dropping those
    # ports. With ufw (which may only allow SSH by default), open them on the robot:
    #   sudo ufw allow from <laptop_ip> to any port 5555 proto tcp   # or: sudo ufw allow 5555/tcp
    #   sudo ufw allow from <laptop_ip> to any port 5556 proto tcp   # or: sudo ufw allow 5556/tcp
    # Verify from the laptop with: nc -zv <robot_ip> 5555 5556  (both should say "succeeded").
    #
    # Dynamic IPs (DHCP): if the router assigns IPs dynamically, the robot's address (remote_ip
    # above) and any IP-restricted ufw rules can break after a reboot/lease change. Re-check the
    # robot's current IP and update both when that happens, or set a DHCP reservation / static IP
    # on the router so the address stays fixed.
    robot.connect()
    keyboard.connect()

    # Init rerun viewer
    init_rerun(session_name="lekiwi_base_teleop")

    if not robot.is_connected or not keyboard.is_connected:
        raise ValueError("Robot or teleop is not connected!")

    print("Starting teleop loop...")
    print("Use keyboard to control the base: WASD for move, ZX for rotate, RF for speed.")

    while True:
        t0 = time.perf_counter()

        # Get robot observation
        observation = robot.get_observation()

        # Get teleop action
        keyboard_keys = keyboard.get_action()
        base_action = robot._from_keyboard_to_base_action(keyboard_keys)

        # Send action to robot
        _ = robot.send_action(base_action)

        # Visualize
        log_rerun_data(observation=observation, action=base_action)

        precise_sleep(max(1.0 / FPS - (time.perf_counter() - t0), 0.0))


if __name__ == "__main__":
    main()
