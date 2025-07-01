import pika
from app.utils.config import load_config

class RabbitMQHelper:
    def __init__(self):
        config = load_config()
        rabbitmq = config["rabbitmq"]
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=rabbitmq.get("host", "localhost"),
                port=rabbitmq.get("port", 5672),
                credentials=pika.PlainCredentials(
                    rabbitmq.get("username", "guest"),
                    rabbitmq.get("password", "guest")
                )
            )
        )
        self.channel = self.connection.channel()
        self.queues_declared = set()

    def declare_queue(self, queue_name):
        if queue_name not in self.queues_declared:
            self.channel.queue_declare(queue=queue_name)
            self.queues_declared.add(queue_name)

    def send_message(self, queue_name, message):
        self.declare_queue(queue_name)
        self.channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=message.encode() if isinstance(message, str) else message
        )

    def close(self):
        self.connection.close()

    # To use as a context manager (with statement)
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()