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


def get_exchange():
    return {
        'exchange': 'mezz-exchange',
        'type': 'fanout'
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
