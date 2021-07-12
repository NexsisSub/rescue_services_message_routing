run:
	docker compose up -d rabbitmq
	docker compose up -d postgres
	sleep 10
	docker compose up -d 

build:
	docker compose build 
config:
	docker-compose -f docker-compose.provision.yml build provision
	docker-compose -f docker-compose.provision.yml run --rm provision