'''
producer / publisher

for rabbitmq fundamental, please visit:
    https://www.cloudamqp.com/blog/2015-05-18-part1-rabbitmq-for-beginners-what-is-rabbitmq.html


rabbitmqctl list_queues name messages_ready messages_unacknowledged
rabbitmqctl list_queues
rabbitmqctl list_exchanges
rabbitmqctl list_bindings
'''


import pika
from params import get_rabbit
from params import get_exchange
from params import get_queuename

exchange = get_exchange()


class Store:
    counter = 0

    @classmethod
    def incr(cls):
        cls.counter += 1
        return cls.counter


class DeliveryMode:
    '''
    refs:
    - https://www.rabbitmq.com/persistence-conf.html
    - https://www.rabbitmq.com/releases/rabbitmq-java-client/current-javadoc/com/rabbitmq/client/MessageProperties.html
    persistent: write to disk as they reach the queue
    transient: only write to disk when evicted from memory
    under memory pressure
    '''
    persistent = 2
    transient = 1


class Producer:
    queuename = {}
    exchange = {}

    def __init__(self):
        channel, connection = get_rabbit()
        self.declare(channel)

        message = '{}....'.format(Store.incr())

        route = self.get_routing(message)
        channel.basic_publish(**route)

        print('Sent content =[{}]'.format(message))
        connection.close()

    def declare(self, channel):
        raise NotImplementedError()

    def get_routing(self, message):
        route = {
            'exchange': self.exchange.get('exchange', ''),
            'routing_key': self.queuename.get('queue', ''),
            'body': message,
            'properties': self.get_properties()
        }
        return route

    def get_properties(self):
        properties = pika.BasicProperties(
            delivery_mode=DeliveryMode.persistent
        )
        return properties


class ProducerQueue(Producer):
    queuename = get_queuename()

    def declare(self, channel):
        channel.queue_declare(**self.queuename)


class ProducerExchange(Producer):
    exchange = get_exchange()

    def declare(self, channel):
        channel.exchange_declare(**self.exchange)


def main():
    ProducerQueue()
    ProducerExchange()


if __name__ == '__main__':
    main()
