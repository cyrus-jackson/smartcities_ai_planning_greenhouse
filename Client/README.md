# Client Component: Smart Greenhouse AI Planning System

This directory contains the Raspberry Pi client for the Smart Greenhouse AI Planning System. The client is responsible for collecting sensor data, controlling actuators, and communicating with the server via RabbitMQ.

For a full system overview and architecture, see the root [README.md](../README.md).

---

## Directory Structure

- `app/` — Client code for hardware modules, state management, and RabbitMQ communication
- `requirements.txt` — Python dependencies for the client

---

## Setup & Running the Client

### Prerequisites
- Raspberry Pi OS (with GPIO support)
- Python 3.9+
- RabbitMQ server accessible from the Pi
- All hardware (fans, servos, sensors) connected to the correct GPIO pins

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Configure GPIO Pins
- Edit `app/config.py` to match your hardware wiring (e.g., `SERVO_1_GPIO`, `SERVO_2_GPIO`)

### Run the Client
```bash
cd app
python client.py
```
- The client will connect to RabbitMQ, listen for commands, and control the hardware accordingly.

---

## Troubleshooting
- Ensure RabbitMQ is running and accessible from the Raspberry Pi.
- If you get `ModuleNotFoundError: No module named 'shared'`, check your working directory or sys.path logic in `state_constants.py`.
- For hardware issues (e.g., servo jitter), see the comments in the relevant module.
- For more details on the system, see the root README.

---

## Author

- Cyrus Jackson
