import pika


def build_params() -> pika.ConnectionParameters:
    credentials = pika.PlainCredentials(
        username='guest',
        password='guest'
    )
    params = pika.ConnectionParameters(
        host='rabbitmq',
        port=5672,
        virtual_host='/',
        credentials=credentials,
        connection_attempts=5,
        socket_timeout=5,
        retry_delay=5
    )
    return params


def get_rabbit():
    params = build_params()
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    return channel, connection


def fanout_exchange():
    return {
        'exchange': 'mezz-fanout-exchange',
        'type': 'fanout'
    }


def direct_exchange():
    return {
        'exchange': 'mezz-direct-exchange',
        'type': 'direct'
    }


def topic_exchange():
    return {
        'exchange': 'mezz-topic-exchange',
        'type': 'topic'
    }


def get_queuename():
    '''
    durable=True ensures task isnt lost even the rabbitmq server restarted,
    which differ from basic_ack (from consumer)
    '''
    return {
        'queue': 'mezz-queue',
        'durable': True
    }


def rpc_queuename():
    return {
        'queue': 'mezz-rpc-queue',
        # 'durable': True
    }


class Tpl:

    _start = ''
    _end = ''
    _tpl = '[{}][{}]:'

    @classmethod
    def start(cls, module_name, *args):
        msg = cls._tpl.format(cls._start, module_name)
        print(msg, *args)

    @classmethod
    def end(cls, module_name, *args):
        msg = cls._tpl.format(cls._end, module_name)
        print(msg, *args)


class ClassNameMixin:

    def __str__(self):
        self_name = self.__class__.__name__
        return '{}'.format(self_name)
