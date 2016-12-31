import sys

import pika

from base_consumer import Consumer
from params import get_queuename
from params import rpc_queuename


class ConsumerQueue(Consumer):

    queuename = get_queuename()

    def declare(self, channel):
        channel.queue_declare(
            **self.queuename
        )

    def consume(self, channel):
        '''
        Rabbitmq dispatch task immediately when the task enter the queue
        Use basic_qos prefetch_count to tell rabbitmq not to give more than N
        messages to a worker at a time.

        In order words, rabbitmq dont dispatch new messages to a worker until
        it has processed and acknowledged the previous messages.
        Instead, it will dispatch it to the next worker that is not still busy.
        '''

        self.queue_name = self.queuename.get('queue')
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
        self.do_task(channel, method, properties, body)
        channel.basic_ack(
            delivery_tag=method.delivery_tag
        )


class ConsumerRPC(ConsumerQueue):

    queuename = rpc_queuename()
    no_ack = False

    def fib(self, n):
        if n == 0:
            return 0
        elif n == 1:
            return 1
        else:
            return self.fib(n - 2) + self.fib(n - 1)

    def callback(self, channel, method, props, body):
        self.tpl.start(str(self), '{} {}'.format(props, body))
        n = int(body)

        ret = self.fib(n)
        channel.basic_publish(
            exchange='',
            routing_key=props.reply_to,
            properties=pika.BasicProperties(
                correlation_id=props.correlation_id
            ),
            body=str(ret)
        )

        '''
        this requires self.no_ack=False or else the consume loop stuck
        '''
        channel.basic_ack(delivery_tag=method.delivery_tag)
        self.tpl.end(str(self), '{} {}'.format(method.delivery_tag, ret))


if __name__ == '__main__':

    mode = sys.argv[1]

    if mode == 'queue':
        ConsumerQueue()
    elif mode == 'queue-ack':
        ConsumerQueueAck()
    elif mode == 'rpc':
        ConsumerRPC()
    else:
        raise ValueError('gg')
