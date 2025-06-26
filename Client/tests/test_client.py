import unittest
from app.rabbitmq_client import RabbitMQClient

class TestRabbitMQClient(unittest.TestCase):
    def setUp(self):
        self.client = RabbitMQClient(queue='test_queue')

    def tearDown(self):
        self.client.close()

    def test_send_and_receive_message(self):
        test_message = "Hello, RabbitMQ!"
        self.client.send_message(test_message)
        received = self.client.receive_message()
        self.assertEqual(received, test_message)

if __name__ == '__main__':
    unittest.main()