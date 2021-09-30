.PHONY : upd-prod upd-dev updc start-db-dev start-db-prod run-dev run-prod build-dev build-prod config

upd-dev:
	docker-compose up -d 

upd-prod:
	docker-compose -f docker-compose.prod.yml  up -d 

updc: 
	docker-compose up -d --build

start-db-dev:
	docker-compose up -d rabbitmq
	docker-compose up -d postgres
	docker-compose up -d elasticsearch

start-db-prod:
	docker-compose -f docker-compose.prod.yml up -d rabbitmq
	docker-compose -f docker-compose.prod.yml up -d postgres
	docker-compose -f docker-compose.prod.yml up -d elasticsearch

run: | start-db-dev config upd-dev

run-prod: | start-db-prod config upd-prod

build-dev:
	docker-compose build 

build-prod:
	docker-compose  -f docker-compose.prod.yml  build 
config:
	docker-compose -f docker-compose.provision.yml build provision
	docker-compose -f docker-compose.provision.yml run --rm provision