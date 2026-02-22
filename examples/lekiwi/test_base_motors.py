#!/usr/bin/env python
"""Quick test: spin each base wheel for 1 second, then stop."""

import time

from lerobot.robots.lekiwi import LeKiwiBase, LeKiwiBaseConfig


def main():
    config = LeKiwiBaseConfig(id="my_lekiwi_base")
    robot = LeKiwiBase(config)
    robot.connect()

    print("Reading current wheel velocities...")
    obs = robot.get_observation()
    print(f"  x.vel={obs['x.vel']:.3f}  y.vel={obs['y.vel']:.3f}  theta.vel={obs['theta.vel']:.3f}")

    try:
        # Spin forward slowly for 2 seconds
        print("\nDriving forward (x=0.1 m/s) for 2 seconds...")
        robot.send_action({"x.vel": 0.1, "y.vel": 0.0, "theta.vel": 0.0})
        time.sleep(2)

        # Read velocities while moving
        obs = robot.get_observation()
        print(f"  x.vel={obs['x.vel']:.3f}  y.vel={obs['y.vel']:.3f}  theta.vel={obs['theta.vel']:.3f}")

        # Rotate in place for 2 seconds
        print("\nRotating (theta=30 deg/s) for 2 seconds...")
        robot.send_action({"x.vel": 0.0, "y.vel": 0.0, "theta.vel": 30.0})
        time.sleep(2)

        # Strafe left for 2 seconds
        print("\nStrafing left (y=0.1 m/s) for 2 seconds...")
        robot.send_action({"x.vel": 0.0, "y.vel": 0.1, "theta.vel": 0.0})
        time.sleep(2)

    finally:
        print("\nStopping...")
        robot.stop_base()
        robot.disconnect()
        print("Done.")


if __name__ == "__main__":
    main()
