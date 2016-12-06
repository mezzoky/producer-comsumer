main: stop up logs

up:
	docker-compose up -d
	docker-compose scale worker=3

build:
	docker-compose build

stop:
	docker-compose stop
	docker-compose rm -f

watch:
	scripts/watch

list:
	# docker-compose exec rabbitmq rabbitmqctl list_queues
	docker-compose exec rabbitmq rabbitmqctl list_queues name messages_ready messages_unacknowledged

restart: stop up

logs:
	COMPOSE_HTTP_TIMEOUT=600000 docker-compose logs -f worker
