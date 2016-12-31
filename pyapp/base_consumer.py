import json
import time

from params import get_rabbit
from params import Notify as BaseNotify
from params import ClassNameMixin


class Notify(BaseNotify):
    endpoint = 'consumer'

    def taking_task(self, *args, **kwargs):
        self._make(self.method.taking_task, *args, **kwargs)

    def completed_task(self, *args, **kwargs):
        self._make(self.method.completed_task, *args, **kwargs)


class Consumer(ClassNameMixin):

    no_ack = True

    def __init__(self):
        self.queue_name = ''
        self.notify = Notify(self)
        channel, connection = get_rabbit()

        self.declare(channel)
        self.consume(channel)

        channel.start_consuming()

    def declare(self, channel):
        raise NotImplementedError()

    def consume(self, channel):
        raise NotImplementedError()

    def unpack(self, data):
        # data is bytes, cannot use str()
        data = data.decode()
        data = json.loads(data)
        id = data['id']
        task = data['task']
        return id, task

    def do_task(self, channel, method, properties, body):

        data = {
            'consumer_tag': method.consumer_tag,
            'delivery_tag': method.delivery_tag,
            'routing_key': method.routing_key,
            'redelivered': method.redelivered,
            'exchange': method.exchange,
            'consumer_delivery_mode': properties.delivery_mode,
            'consumer_correlation_id': properties.correlation_id,
            'consumer_reply_to': properties.reply_to,
        }

        id, task = self.unpack(body)
        self.notify.taking_task(
            id,
            task=task,
            queue=self.queue_name,
            ack=not self.no_ack,
            **data
        )
        time.sleep(task.count('.'))
        self.notify.completed_task(
            id,
            task=task,
            queue=self.queue_name,
            ack=not self.no_ack
        )

    def callback(self, channel, method, properties, body):
        self.do_task(channel, method, properties, body)
