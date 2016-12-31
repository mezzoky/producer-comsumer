'''
producer / publisher

for rabbitmq fundamental, please visit:
    https://www.cloudamqp.com/blog/2015-05-18-part1-rabbitmq-for-beginners-what-is-rabbitmq.html


rabbitmqctl list_queues name messages_ready messages_unacknowledged
rabbitmqctl list_queues
rabbitmqctl list_exchanges
rabbitmqctl list_bindings
'''

import json
import uuid

import pika

from params import get_rabbit
from params import rpc_queuename
from params import Notify as BaseNotify
from params import ClassNameMixin


class Store:
    counter = ''

    @classmethod
    def incr(cls):
        cls.counter = str(uuid.uuid4())
        return cls.counter


class DeliveryMode:
    '''
    refs:
    - https://www.rabbitmq.com/persistence-conf.html
    - https://www.rabbitmq.com/releases/rabbitmq-java-client\
            /current-javadoc/com/rabbitmq/client/MessageProperties.html
    persistent: write to disk as they reach the queue
    transient: only write to disk when evicted from memory
    under memory pressure
    '''
    persistent = 2
    transient = 1


class Notify(BaseNotify):
    endpoint = 'producer'

    def delivering_task(self, *args, **kwargs):
        self._make(self.method.delivering_task, *args, **kwargs)

    def delivered_task(self, *args, **kwargs):
        self._make(self.method.delivered_task, *args, **kwargs)


class Producer(ClassNameMixin):
    exchange = {}
    routing_key = ''

    def __init__(self):
        self.notify = Notify(self)
        channel, connection = get_rabbit()
        self.run(channel, connection)

    def run(self, channel, connection):
        self.declare(channel)

        task, id = self.gen_task()

        route = self.get_routing(task)
        self.notify.delivering_task(
            id,
            task=task,
            **route
        )
        channel.basic_publish(**route)

        self.notify.delivered_task(id)
        connection.close()

    def declare(self, channel):
        raise NotImplementedError()

    def get_routing(self, body):
        route = {
            'exchange': self.exchange.get('exchange', ''),
            'routing_key': self.routing_key,
            'body': body,
            'properties': self.get_properties()
        }
        return route

    def get_properties(self):
        properties = pika.BasicProperties(
            delivery_mode=DeliveryMode.persistent
        )
        return properties

    @classmethod
    def gen_task(self):
        counter = Store.incr()
        message = json.dumps({
            'task': 'tsk ......',
            'id': counter,
        })
        return message, counter


class ProducerRPC(Producer):

    routing_key = rpc_queuename().get('queue')

    def __init__(self):

        self.queue_name = ''
        self.corr_id = ''
        self.response = None
        self.channel = None
        self.connection = None

        super(ProducerRPC, self).__init__()

    def run(self, channel, connection):
        result = channel.queue_declare(exclusive=True)
        self.queue_name = result.method.queue

        channel.basic_consume(
            self.on_response,
            no_ack=True,
            queue=self.queue_name
        )

        self.channel = channel
        self.connection = connection

    def on_response(self, channel, method, props, body):
        # Tpl.end(str(self), 'x::Received fib = {} {} {}'.format(
        #    body, self.corr_id, props.correlation_id
        # ))
        if self.corr_id == props.correlation_id:
            # Tpl.end(str(self), 'Received fib = {}'.format(body))
            self.response = body

    def call(self, n):
        self.corr_id = str(uuid.uuid4())
        routing = self.get_routing(str(n))
        # Tpl.start(str(self), task='Requesting fib({} {})'.format(n, routing))

        self.channel.basic_publish(
            **routing
        )
        while self.response is None:
            self.connection.process_data_events()

        return int(self.response)

    def get_properties(self):
        properties = pika.BasicProperties(
            delivery_mode=DeliveryMode.persistent,
            reply_to=self.queue_name,
            correlation_id=self.corr_id
        )
        return properties
