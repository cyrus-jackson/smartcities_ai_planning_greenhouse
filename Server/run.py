# run.py

from app import app
import app.tasks as tasks 
if __name__ == '__main__':
    # Start the batch consumer as a background task
    tasks.rabbitmq_batch_consumer.delay()
    result = tasks.long_running_task.delay(5, 7)
    app.run()

