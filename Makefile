main: fstop up logs

up:
	docker-compose up -d web
	docker-compose up -d
	# docker-compose scale queue-worker=2 exchange-worker=2

build:
	docker-compose build

stop:
	docker-compose stop
	docker-compose rm -f

fstop:
	docker ps -qa | xargs -i docker rm -f {}

watch:
	bin/watch

list:
	# docker-compose exec rabbitmq rabbitmqctl list_queues
	docker-compose exec rabbitmq rabbitmqctl list_queues name messages_ready messages_unacknowledged

restart: stop up

logs:
	COMPOSE_HTTP_TIMEOUT=600000 docker-compose logs -f | grep -v rabbitmq

test:
	bin/test
