import sys

from consumer_exchange import ConsumerExchange
from params import direct_exchange


class ConsumerDirectExchange(ConsumerExchange):
    '''
    It is legal to bind multiple direct exchange queues
    with the same binding key.
    In that case, the direct exchange will behave like `fanout` and
    will broadcast the message to all the matching queues.

    producer producer1{exchange: direct, routing_key: A, message: 'test'}
    consumer queue1{exchange: direct, routing_key: A}
    consumer queue2{exchange: direct, routing_key: A}
    A message with routing key A will be delivered to both queue1 and queue2.
    '''
    exchange = direct_exchange()
    routing_keys = []

    def bind(self, channel, queue_name):
        for key in self.routing_keys:
            channel.queue_bind(
                exchange=self.exchange.get('exchange'),
                queue=queue_name,
                routing_key=key
            )

    def callback(self, channel, method, properties, body):
        _body = '{} queue: {} key: {}'.format(
            body,
            self.queue_name,
            method.routing_key
        )
        self.do_task(_body)


class TypeA(ConsumerDirectExchange):
    routing_keys = ['typeA']


class TypeB(ConsumerDirectExchange):
    routing_keys = ['typeB']


class TypeC(ConsumerDirectExchange):
    routing_keys = ['typeC']


class TypeAny(ConsumerDirectExchange):
    routing_keys = ['typeA', 'typeB', 'typeC']

if __name__ == '__main__':
    type_ = sys.argv[1]

    if type_.lower() == 'a':
        TypeA()
    elif type_.lower() == 'b':
        TypeB()
    elif type_.lower() == 'c':
        TypeC()
    elif type_.lower() == 'any':
        TypeAny()
    else:
        raise ValueError('direct exchange needs one argument for routing key')
