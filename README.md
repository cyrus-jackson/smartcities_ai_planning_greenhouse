# Smart Greenhouse AI Planning System

This project is a smart greenhouse control and monitoring system using AI planning, indirect communication via RabbitMQ, and a modular Python codebase. The system is split into two main components:

- **Server**: Flask web server for dashboard, control panel, and planning logic (runs on your main computer/server)
- **Client**: Hardware interface and actuator control (runs on a Raspberry Pi inside the greenhouse)

## How It Works


- The **Server** provides a web dashboard for monitoring and controlling the greenhouse. It exposes endpoints for sensor data, configuration, and manual control.
- When a user triggers an action (e.g., turn on fan, open roof), the server sends a message to a RabbitMQ queue.
- The **Client** (on the Raspberry Pi) listens to this queue, receives action commands, and interacts with the hardware (fans, servos, pumps, sensors).
- Sensor data is collected by the client and sent to the server for logging and visualization.
- The server uses **Redis** for:
  - Real-time notifications (pushing alerts and updates to the dashboard)
  - Locking mechanisms (to prevent race conditions and ensure safe concurrent operations)
- All configuration and state constants are shared via a single `shared/state_constants.py` file.

This indirect communication (decoupling) via RabbitMQ (and Redis for notifications/locking) allows the server and client to run independently, even on different machines or networks.
## Redis Usage (Server)

- The server uses Redis for two main purposes:
  1. **Notifications**: Real-time alerts and updates are pushed to the dashboard using Redis pub/sub or as a fast in-memory store.
  2. **Locking**: Redis is used to implement distributed locks, ensuring that only one process or thread can perform certain critical operations at a time (e.g., actuator commands, config updates).

- Make sure Redis is running and accessible before starting the server.

---

---

## Server Setup & Usage

### Prerequisites
- Python 3.9+
- PostgreSQL
- RabbitMQ
- (Recommended) Create a virtual environment

### Install Dependencies
```
cd Server
pip install -r requirements.txt
```

### Database Setup
1. Start PostgreSQL and RabbitMQ services.
2. Create the database and tables:
   ```
   python ../createdb.py
   ```
   (This will also initialize default configs.)

### Run the Server
```
cd Server
python -m run
```
- The web dashboard will be available at `http://localhost:5000`.

---

## Client (Raspberry Pi) Setup & Usage

### Prerequisites
- Raspberry Pi OS (with GPIO support)
- Python 3.9+
- RabbitMQ server accessible from the Pi
- All hardware (fans, servos, sensors) connected to the correct GPIO pins

### Install Dependencies
```
cd Client
pip install -r requirements.txt
```

### Configure GPIO Pins
- Edit `Client/app/config.py` to match your hardware wiring (e.g., `SERVO_1_GPIO`, `SERVO_2_GPIO`)

### Run the Client
```
cd Client/app
python client.py
```
- The client will connect to RabbitMQ, listen for commands, and control the hardware accordingly.

---

## Indirect Communication (RabbitMQ)

- The server and client do **not** communicate directly.
- The server sends action commands (as JSON) to a RabbitMQ queue (e.g., `planner_queue`).
- The client subscribes to this queue, receives commands, and executes them on the hardware.
- This architecture allows for robust, decoupled, and scalable operation.

---

## Directory Structure

```
smartcities_ai_planning_greenhouse/
├── Server/           # Flask server, planning logic, dashboard
├── Client/           # Raspberry Pi client, hardware modules
├── shared/           # Shared constants and code
├── createdb.py       # Database/table/config initialization
```

---

## Troubleshooting
- Ensure RabbitMQ and PostgreSQL are running and accessible from both server and client.
- If you get `ModuleNotFoundError: No module named 'shared'`, make sure you are running scripts from the correct directory, or check the sys.path logic in `state_constants.py`.
- For hardware issues (e.g., servo jitter), see the comments in the relevant module.

---

## Authors
- Cyrus Jackson

---

## License
MIT License