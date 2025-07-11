# run.py

from app import app
from app.tasks import *
from apscheduler.schedulers.background import BackgroundScheduler
import signal
import sys

if __name__ == '__main__':

    # Start the batch consumer as a managed thread
    start_rabbitmq_batch_consumer()
    start_rabbitmq_state_consumer()

    # Schedule long_running_task to run every 20 seconds
    scheduler = BackgroundScheduler()
    scheduler.add_job(long_running_task, 'interval', seconds=150, args=[5, 7])

    # Schedule weather fetch every hour
    scheduler.add_job(fetch_weather_forecast, 'interval', minutes=20)
    
    scheduler.start()

    def cleanup(signum=None, frame=None):
        print("Shutting down server and cleaning up threads...")
        stop_rabbitmq_batch_consumer()
        stop_rabbitmq_state_consumer()
        scheduler.shutdown()
        sys.exit(0)

    # Handle SIGINT/SIGTERM for graceful shutdown
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    # Reset all Notifications
    reset_notifications()
    app.run()

