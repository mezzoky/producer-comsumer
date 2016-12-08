import time

from params import get_rabbit
from params import get_exchange
from params import get_queuename


class Consumer:

    no_ack = True

    def __init__(self):
        channel, connection = get_rabbit()
        self.declare(channel)

        '''
        Rabbitmq dispatch task immediately when the task enter the queue
        Use basic_qos prefetch_count to tell rabbitmq not to give more than N
        messages to a worker at a time.
        In order words, rabbitmq dont dispatch new messages to a worker until
        it has processed and acknowledged the previous messages.
        Instead, it will dispatch it to the next worker that is not still busy.
        '''
        self.consume(channel)
        channel.start_consuming()

    def work(self, body):
        module_name = self.__class__.__name__
        print('{} taking work'.format(module_name), body)
        time.sleep(body.count(b'.'))
        print('{} work done'.format(module_name), body)

    def declare(self, channel):
        raise NotImplementedError()

    def callback(self, channel, method, properties, body):
        self.work(body)


class ConsumerQueue(Consumer):

    queuename = get_queuename()

    def declare(self, channel):
        channel.queue_declare(
            **self.queuename
        )

    def consume(self, channel):
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(
            self.callback,
            queue=self.queuename.get('queue'),
            no_ack=self.no_ack
        )


class ConsumerQueueAck(ConsumerQueue):

    no_ack = False

    def callback(self, channel, method, properties, body):
        '''
        even if you kill a worker while it was processing a message,
        nothing will be lost.
        Soon after the worker dies all unacknowledged messages will be
        redelivered.
        '''
        self.work(body)
        channel.basic_ack(
            delivery_tag=method.delivery_tag
        )


class ConsumerExchange(Consumer):

    exchange = get_exchange()

    def consume(self, channel):
        '''
        exclusive=True: once we disconnect the consumer the queue should be deleted.
        '''
        result = channel.queue_declare(exclusive=True)
        queue_name = result.method.queue

        '''
        Now we need to tell the exchange to send messages to our queue.
        That relationship between exchange and a queue is called a binding.
        '''
        channel.queue_bind(
            exchange=self.exchange.get('exchange'),
            queue=queue_name
        )
        channel.basic_consume(
            self.callback,
            queue=queue_name,
            no_ack=self.no_ack
        )

    def declare(self, channel):
        channel.exchange_declare(**self.exchange)
