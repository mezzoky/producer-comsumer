import time

import pika

from params import build_params


def ack_callback(channel, method, properties, body):
    '''
    even if you kill a worker while it was processing a message,
    nothing will be lost.
    Soon after the worker dies all unacknowledged messages will be redelivered.
    '''
    work(body)
    channel.basic_ack(delivery_tag=method.delivery_tag)


def callback(channel, method, properties, body):
    work(body)


def work(body):
    print('taking work', body)
    time.sleep(body.count(b'.'))
    print('work done', body)


def ack_consume(channel):
    channel.basic_consume(
        ack_callback,
        queue='mezzoky',
        no_ack=False
    )


def consume(channel):
    channel.basic_consume(
        callback,
        queue='mezzoky',
        no_ack=True
    )


def consumer():
    params = build_params()

    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue='mezzoky', durable=True)

    '''
    Rabbitmq dispatch task immediately when the task enter the queue
    Use basic_qos prefetch_count to tell rabbitmq not to give more than N
    messages to a worker at a time.
    In order words, rabbitmq dont dispatch new messages to a worker until
    it has processed and acknowledged the previous messages.
    Instead, it will dispatch it to the next worker that is not still busy.
    '''
    channel.basic_qos(prefetch_count=1)
    ack_consume(channel)
    channel.start_consuming()


def main():
    consumer()


if __name__ == '__main__':
    main()
