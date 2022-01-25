from click.core import Command
from kombu import Connection
from kombu.entity import Queue

connection = Connection(hostname="southpole.icetestng.com", userid="icecompass", password="n-6TaDR-zRErUBF7U@qQ", virtual_host="southpole")

connection.connect()
print (f"Connected to RabbitMQ: {connection.connected}")

def callback(body, message):
    print (body, message)

with connection as connection:
    queue = Queue('icecompass', routing_key='icecompass')
    consumer = connection.Consumer(queue)
    consumer.register_callback(callback)