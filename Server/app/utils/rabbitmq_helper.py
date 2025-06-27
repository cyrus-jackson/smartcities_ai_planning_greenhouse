import pika
from app.utils.config import load_config

class RabbitMQHelper:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            config = load_config()
            rabbitmq = config["rabbitmq"]
            cls._instance = super().__new__(cls)
            cls._instance.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=rabbitmq.get("host", "localhost"),
                    port=rabbitmq.get("port", 5672),
                    credentials=pika.PlainCredentials(
                        rabbitmq.get("username", "guest"),
                        rabbitmq.get("password", "guest")
                    )
                )
            )
            cls._instance.channel = cls._instance.connection.channel()
            cls._instance.queues_declared = set()
        return cls._instance

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