'''
producer / publisher

for rabbitmq fundamental, please visit:
    https://www.cloudamqp.com/blog/2015-05-18-part1-rabbitmq-for-beginners-what-is-rabbitmq.html



RabbitMQ
- producer -> exchange -> queue
'''
import sys
import pika
from params import build_params


class DeliveryMode:
    persistent = 2
    transient = 1


def get_routing():
    '''
    refs:
        - https://www.rabbitmq.com/persistence-conf.html
        - https://www.rabbitmq.com/releases/rabbitmq-java-client/current-javadoc/com/rabbitmq/client/MessageProperties.html
    persistent: write to disk as they reach the queue
    transient: only write to disk when evicted from memory under memory pressure
    '''
    body = len(sys.argv) > 1 and sys.argv[1] or '.............'
    properties = pika.BasicProperties(delivery_mode=DeliveryMode.persistent)
    route = {
        'exchange': '',
        'routing_key': 'mezzoky',
        'body': body,
        'properties': properties
    }
    return route


def producer():
    params = build_params()

    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    '''
    durable=True ensures task isnt lost even the rabbitmq server restarted,
    which differ from basic_ack (from consumer)
    '''
    channel.queue_declare(queue='mezzoky', durable=True)

    route = get_routing()
    channel.basic_publish(**route)
    print('sent')

    connection.close()


def main():
    producer()


if __name__ == '__main__':
    main()
