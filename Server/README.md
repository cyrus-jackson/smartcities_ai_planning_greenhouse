## Project Structure

The project is organized as follows:

- `app/`: Contains the Flask application and routes.
- `tests/`: Houses unit tests for the application.
- `run.py`: A script to run the Flask application.

## Getting Started



1. **Install Dependencies:**

   Install the necessary dependencies using `pip`:

   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application:**

   Start the Flask application:

   ```bash
   From the directory: smartcities_ai_planning_greenhouse\Server
## Server Component: Smart Greenhouse AI Planning System

This directory contains the Flask server for the Smart Greenhouse AI Planning System. The server provides the dashboard, control panel, planning logic, and APIs for the greenhouse.

For a full system overview and architecture, see the root [README.md](../README.md).

---

### Directory Structure

- `app/` — Flask application code, routes, and logic
- `tests/` — Unit tests for the server
- `run.py` — Script to start the Flask server
- `requirements.txt` — Python dependencies

---

## Setup & Running the Server

### Prerequisites
- Python 3.9+
- PostgreSQL
- RabbitMQ
- Redis

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Database Setup
1. Start PostgreSQL, RabbitMQ, and Redis services.
2. Initialize the database and tables from the project root:
   ```bash
   python ../createdb.py
   ```
   (This will also initialize default configs.)

### Run the Server
```bash
cd Server
python -m run
```
- The web dashboard will be available at [http://localhost:5001](http://localhost:5001).

---

## Running Server Tests

To run all unit tests:
```bash
python -m unittest discover tests
```

---

## Troubleshooting
- Ensure PostgreSQL, RabbitMQ, and Redis are running and accessible.
- If you get `ModuleNotFoundError: No module named 'shared'`, check your working directory or sys.path logic in `state_constants.py`.
- For more details on the system, see the root README.

---

## Author

- Cyrus Jackson

