import time

from params import get_rabbit
from params import Tpl as BaseTpl
from params import ClassNameMixin


class Tpl(BaseTpl):
    _start = 'TAKE TASK'
    _end = 'COMPLETE TASK'


class Consumer(ClassNameMixin):
    tpl = Tpl
    no_ack = True

    def __init__(self):
        channel, connection = get_rabbit()

        self.declare(channel)
        self.consume(channel)

        channel.start_consuming()

    def declare(self, channel):
        raise NotImplementedError()

    def consume(self, channel):
        raise NotImplementedError()

    def do_task(self, body):
        if isinstance(body, bytes):
            body = str(body)
        Tpl.start(str(self), body)
        time.sleep(body.count('.'))
        Tpl.end(str(self), body)

    def callback(self, channel, method, properties, body):
        self.do_task(str(body))
