from base_producer import Producer
from base_producer import ProducerRPC
from params import get_queuename
from params import fanout_exchange
from params import direct_exchange
from params import topic_exchange


class ProducerQueue(Producer):
    queuename = get_queuename()
    routing_key = queuename.get('queue')

    def declare(self, channel):
        channel.queue_declare(**self.queuename)


class ProducerExchange(Producer):
    exchange = fanout_exchange()
    routing_key = ''

    def declare(self, channel):
        channel.exchange_declare(**self.exchange)


class ProducerDirectExchange(ProducerExchange):
    exchange = direct_exchange()
    routing_key = 'typeA'


class ProducerDirectExchangeB(ProducerDirectExchange):
    routing_key = 'typeB'


class ProducerDirectExchangeC(ProducerDirectExchange):
    routing_key = 'typeC'


class ProducerTopicExchange(ProducerExchange):
    exchange = topic_exchange()
    routing_key = 'kern.critical'


if __name__ == '__main__':
    ProducerQueue()
    ProducerExchange()
    # ProducerDirectExchange()
    # ProducerDirectExchangeB()
    # ProducerDirectExchangeC()
    # ProducerTopicExchange()

    # rpc = ProducerRPC()
    # rpc.call(5)
