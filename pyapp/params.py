import socket
import json
from urllib import request
from urllib import parse

import pika


def build_params():
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


class Method:
    server_ready = 'server_ready'
    server_shutdown = 'server_shutdown'
    delivering_task = 'delivering_task'
    delivered_task = 'delivered_task'
    taking_task = 'taking_task'
    completed_task = 'completed_task'


class Notify:
    endpoint = ''
    method = Method

    def __init__(self, target_instance):
        self.module = target_instance
        self.name = str(target_instance)

    def _send(self, method, data):
        data = {
            'payload': json.dumps(data),
            'method': method,
        }
        encoded = parse.urlencode(data)
        url = 'http://web:8888/{}'.format(self.endpoint)
        url += '?' + encoded
        request.urlopen(url)

    def _make(self, method, id, task=None, **kwargs):
        data = {
            'hostname': socket.gethostname(),
            'module': self.name,
            'id': id,
            'status': method,
        }

        if task is not None:
            data['task'] = task

        properties = kwargs.pop('properties', None)
        if properties:
            data['delivery_mode'] = properties.delivery_mode
            data['reply_to'] = properties.reply_to
            data['correlation_id'] = properties.correlation_id

        data.update(kwargs)
        self._send(method, data)

    def server_ready(self, *args, **kwargs):
        self._make(self.method.server_ready, *args, **kwargs)

    def server_shutdown(self, *args, **kwargs):
        self._make(self.method.server_shutdown, *args, **kwargs)


class ClassNameMixin:

    def __str__(self):
        self_name = self.__class__.__name__
        return '{}'.format(self_name)
