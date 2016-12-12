from base_consumer import Consumer
from params import fanout_exchange


class ConsumerExchange(Consumer):

    exchange = fanout_exchange()

    def __init__(self):
        self.queue_name = ''
        super(ConsumerExchange, self).__init__()

    def declare(self, channel):
        channel.exchange_declare(**self.exchange)

    def consume(self, channel):
        '''
        exclusive=True: once we disconnect the consumer,
        the queue should be deleted.
        '''
        result = channel.queue_declare(exclusive=True)
        '''
        Now we need to tell the exchange to send messages to our queue.
        That relationship between exchange and a queue is called a binding.
        '''
        queue_name = result.method.queue
        self.queue_name = queue_name

        self.bind(channel, queue_name)

        channel.basic_consume(
            self.callback,
            queue=queue_name,
            no_ack=self.no_ack
        )

    def bind(self, channel, queue_name):
        channel.queue_bind(
            exchange=self.exchange.get('exchange'),
            queue=queue_name
        )

if __name__ == '__main__':
    ConsumerExchange()
