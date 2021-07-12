.PHONY : up upd updc start-db run build config
up:
	docker compose up

upd:
	docker compose up -d 

updc: 
	docker compose up -d --build

start-db:
	docker compose up -d rabbitmq
	docker compose up -d postgres
run: | start-db wait-for-startup config upd

wait-for-startup:
	sleep 10
build:
	docker compose build 
config:
	docker-compose -f docker-compose.provision.yml build provision
	docker-compose -f docker-compose.provision.yml run --rm provision