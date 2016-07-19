

import os
import json
import pika
import logging
import requests


logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# App Settings
RABBITMQ_SERVER = os.environ.get('RABBITMQ_SERVER', 'rabbitmq-alpha')

# RabbitMQ Setup
connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_SERVER))
channel = connection.channel()

channel.exchange_declare(exchange='regner', type='topic')
channel.queue_declare(queue='slack-send-webhooks', durable=True)
channel.queue_bind(exchange='regner', queue='slack-send-webhooks', routing_key='slack.send.webhook')
logger.info('Connected to RabbitMQ server...')


def callback(ch, method, properties, body):
    data = json.loads(body.decode())
    response = requests.post(data['webhook'], data=json.dumps(data['message']))

    if response.status_code == requests.codes.ok:
        ch.basic_ack(delivery_tag = method.delivery_tag)
    else:
        logger.info(response.text)
        print(response.headers, response)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback, queue='slack-send-webhooks')
channel.start_consuming()
