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
