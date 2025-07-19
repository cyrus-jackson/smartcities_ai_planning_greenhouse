# run.py

from app import app
from app.tasks import *
from apscheduler.schedulers.background import BackgroundScheduler
import signal
import sys
import logging

if __name__ == '__main__':
    # --- Logging Configuration ---
    # Configure root logger to show INFO level messages
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Set Pika logger to WARNING to reduce noise from connection heartbeats, etc.
    logging.getLogger("pika").setLevel(logging.WARNING)
    # --- End Logging Configuration ---

    # Start the batch consumer as a managed thread
    start_rabbitmq_batch_consumer()
    start_rabbitmq_state_consumer()

    # Schedule long_running_task to run every 20 seconds
    scheduler = BackgroundScheduler()
    scheduler.add_job(long_running_task, 'interval', seconds=20, args=[5, 7])

    # Schedule weather fetch every hour
    scheduler.add_job(fetch_weather_forecast, 'interval', seconds=20)
    
    scheduler.start()

    def cleanup(signum=None, frame=None):
        logging.info("Shutting down server and cleaning up threads...")
        stop_rabbitmq_batch_consumer()
        stop_rabbitmq_state_consumer()
        scheduler.shutdown()
        sys.exit(0)

    # Handle SIGINT/SIGTERM for graceful shutdown
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    # Reset all Notifications
    reset_notifications()
    app.run(port=5001)

