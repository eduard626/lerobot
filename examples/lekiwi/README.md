# LeKiwi Examples

LeKiwi is a three-omniwheel mobile robot that can optionally include an SO-100 follower arm. It uses a host/client architecture: a **host** script runs on the robot's onboard computer (e.g. Raspberry Pi) and a **client** script runs on your laptop, communicating over ZMQ.

## Configurations

| Configuration | Robot type | Client type | Motors | Cameras | Use case |
|---|---|---|---|---|---|
| **Full robot** | `lekiwi` | `lekiwi_client` | 6 arm + 3 base | front + wrist | Mobile manipulation with arm + base |
| **Base only** | `lekiwi_base` | `lekiwi_base_client` | 3 base | front | Navigation and base control experiments |

## Usage

### Full robot (arm + base)

**On the robot (host):**
```bash
python -m lerobot.robots.lekiwi.lekiwi_host --robot.id=my_lekiwi
```

**On your laptop (client):**
```bash
python examples/lekiwi/teleoperate.py
```

This uses a leader arm (SO-100) for arm teleoperation and keyboard (WASD/ZX) for base control.

### Base only

**On the robot (host):**
```bash
python -m lerobot.robots.lekiwi.lekiwi_host --robot.type=lekiwi_base --robot.id=my_lekiwi_base
```

**On your laptop (client):**
```bash
python examples/lekiwi/teleoperate_base.py
```

This uses keyboard only (WASD for movement, ZX for rotation, RF for speed).

## Examples overview

| Script | Description |
|---|---|
| `teleoperate.py` | Full robot teleoperation (leader arm + keyboard) |
| `teleoperate_base.py` | Base-only teleoperation (keyboard only) |
| `record.py` | Record a dataset while teleoperating |
| `replay.py` | Replay a recorded dataset on the robot |
| `evaluate.py` | Evaluate a trained policy on the robot |

## Notes

- Replace `remote_ip` in the client scripts with the actual IP address of your robot.
- The host defaults to `--robot.type=lekiwi` (full robot). Pass `--robot.type=lekiwi_base` for base-only mode.
- The host session defaults to 30 seconds (`connection_time_s=30`), after which it prints "Cycle time reached" and shuts down. Increase this for longer sessions:
  ```bash
  python -m lerobot.robots.lekiwi.lekiwi_host --robot.type=lekiwi_base --robot.id=my_lekiwi_base --host.connection_time_s=3600
  ```
- Motor IDs: arm uses 1-6, base wheels use 7 (left), 8 (back), 9 (right).
- Keyboard controls: W/S forward/back, A/D strafe, Z/X rotate, R/F speed up/down, Q quit.
