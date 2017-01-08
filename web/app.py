import os
import logging
import json
from collections import OrderedDict
from collections import defaultdict

from tornado import websocket
from tornado import web
from tornado import ioloop

from tornado import options


class Channel:
    chans = set()
    all = chans
    serializer = json.dumps
    deserializer = json.loads

    @classmethod
    def add(cls, chan):
        cls.chans.add(chan)
        # logging.info('latest pool: %s', cls.chans)

    @classmethod
    def remove(cls, chan):
        cls.chans.remove(chan)
        # logging.info('latest pool: %s', cls.chans)

    @classmethod
    def pub(cls, msg):
        msg = cls.serializer(msg)
        for chan in cls.chans:
            chan.write_message(msg)


class NotTypeError(TypeError):
    def __init__(self, field, val, exp_type, *args, **kwargs):
        message = 'Field (%s %s) Must be the type of (%s)' % (
            field,
            type(val).__name__,
            exp_type.__name__
        )
        self.message = message
        super(NotTypeError, self).__init__(message, *args, **kwargs)


class FieldError(TypeError):
    def __init__(self, field, *args, **kwargs):
        message = 'field (%s) is not registered on the DB' % field
        self.message = message
        super(FieldError, self).__init__(message, *args, **kwargs)


class Row:
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            if not hasattr(self, key):
                raise FieldError(key)
            self_val = getattr(self, key)
            if type(val) is not self_val and val is not None:
                raise NotTypeError(key, val, self_val)
            setattr(self, key, val)

        fields = [
            f for f in self.__class__.__dict__.keys()
            if not f.startswith('__') and not f.endswith('__')
        ]
        self_fields = vars(self)
        for f in fields:
            if f not in self_fields:
                setattr(self, f, None)

    @property
    def cursor(self):
        return vars(self)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.cursor)


class CommonFields:
    id = str
    module = str
    hostname = str
    exchange = str
    body = str
    task = str
    delivery_mode = int
    reply_to = str
    correlation_id = str
    status = str
    routing_key = str


class Producer(CommonFields, Row):
    pass


class Consumer(CommonFields, Row):
    queue = str
    ack = bool

    consumer_tag = str
    delivery_tag = str
    routing_key = str
    redelivered = str
    exchange = str

    consumer_delivery_mode = str
    consumer_correlation_id = str
    consumer_reply_to = str


class BaseManager:
    key = 'id'
    model = None
    task = OrderedDict()

    def __init__(self):
        # unique ordered element data structure
        self.hosts = defaultdict(OrderedDict)

    def register(self, **kwargs):
        key = kwargs.get(self.key, None)
        if not key:
            raise ValueError('%s is missing' % self.key)

        if key not in self.task:
            row = self.model(**kwargs)
            self.task[key] = row.cursor

            hostname = row.hostname
            self.hosts[hostname][row.id] = 1 << 0
        return self.task[key]

    def update(self, **kwargs):
        key = kwargs.get(self.key, None)
        data = self.task[key]
        data.update(**kwargs)
        hostname = data['hostname']
        self.hosts[hostname][data['id']] = 1 << 0
        return self.task[key]

    @property
    def data(self):
        hosts = {}
        for k, v in self.hosts.items():
            hosts[k] = [i for i in v.keys()]
        # logging.info(self.hosts)
        return hosts


class Producers(BaseManager):
    model = Producer


class Consumers(BaseManager):
    model = Consumer


class HomePageHandler(web.RequestHandler):
    def get(self):
        self.render('index.html', channels=[])


class ProducerHandler(web.RequestHandler):
    producers = Producers()

    def get(self):
        payload = self.get_argument('payload')
        method = self.get_argument('method')

        payload = json.loads(payload)

        if method == 'delivering_task':
            ret = self.producers.register(**payload)
        elif method == 'delivered_task':
            ret = self.producers.update(**payload)

        # race condition due to Consumer and Producer share task class variable
        # ret['hostname'] = payload['hostname']
        data = {
            'method': method,
            'data': ret
        }
        Channel.pub(data)


class WorkerHandler(web.RequestHandler):
    consumers = Consumers()

    def get(self):

        payload = self.get_argument('payload')
        method = self.get_argument('method')

        payload = json.loads(payload)

        if method in ('completed_task', 'taking_task'):
            ret = self.consumers.update(**payload)

        # race condition due to Consumer and Producer share task class variable
        # ret['hostname'] = payload['hostname']
        data = {
            'method': method,
            'data': ret
        }
        Channel.pub(data)


class WebSocketHandler(websocket.WebSocketHandler):
    id = 1

    def incr(self):
        self.id = WebSocketHandler.id
        WebSocketHandler.id += 1

    def open(self):
        self.incr()
        Channel.add(self)

        data = {
            'method': 'initialize',
            'data': {
                'tasks': ProducerHandler.producers.task,
                'producer_hosts': ProducerHandler.producers.data,
                'consumer_hosts': WorkerHandler.consumers.data,
            }
        }

        Channel.pub(data)

    def on_message(self, message):
        pass

    def on_close(self):
        Channel.remove(self)

    def get_compression_options(self):
        # TODO: study this
        # Non-None enables compression with default options.
        return {}

    def check_origin(self, origin):
        # TODO: study this
        return True

    def __repr__(self):
        return str(self)

    def __str__(self):
        return 'id({})'.format(self.id)


class App(web.Application):
    def __init__(self):
        handlers = [
            (r'/', HomePageHandler),
            (r'/ws', WebSocketHandler),
            (r'/producer', ProducerHandler),
            (r'/consumer', WorkerHandler),
        ]

        base = os.path.dirname(__file__)
        settings = {
            'cookie_secret': 'secret',
            'template_path': os.path.join(base, 'templates'),
            'static_path': os.path.join(base, 'static'),
            'debug': True,
            'xsrf_cookies': True,
        }
        super(App, self).__init__(handlers, **settings)


if __name__ == '__main__':
    # just want to auto enable the tornado.log feature
    options.parse_command_line()

    app = App()
    app.listen(8888)
    ioloop.IOLoop.current().start()
