import sys

from consumer_exchange import ConsumerExchange
from params import topic_exchange


class ConsumerTopicExchange(ConsumerExchange):
    '''
    The binding key must also be in the same form.
    The logic behind the topic exchange is similar to a direct one
    - a message sent with a particular routing key will be delivered
    to all the queues that are bound with a matching binding key


    Topic exchange is powerful and can behave like other exchanges.

    When a queue is bound with "#" (hash) binding key
    - it will receive all the messages,
    regardless of the routing key - like in fanout exchange.

    When special characters "*" (star) and "#" (hash) aren't used in bindings,
    the topic exchange will behave just like a direct one.
    '''
    exchange = topic_exchange()
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


class Any(ConsumerTopicExchange):
    '''
    * (star) can substitute for exactly one word.
    # (hash) can substitute for zero or more words.
    '''
    routing_keys = ['#']


class Kern(ConsumerTopicExchange):
    routing_keys = ['kern.*']


class Critical(ConsumerTopicExchange):
    routing_keys = ['*.critical']


class KernOrCritical(ConsumerTopicExchange):
    routing_keys = ['kern.*', '*.critical']

if __name__ == '__main__':
    type_ = sys.argv[1]

    if type_.lower() == 'kern':
        Kern()
    elif type_.lower() == 'critical':
        Critical()
    elif type_.lower() == 'kerncritical':
        KernOrCritical()
    elif type_.lower() == 'any':
        Any()
    else:
        raise ValueError('direct exchange needs one argument for routing key')
