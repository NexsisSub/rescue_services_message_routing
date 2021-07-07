publish-message:
	docker-compose -f docker-compose.provision.yml run --rm publisher
config:
	docker-compose -f docker-compose.provision.yml build provision
	docker-compose -f docker-compose.provision.yml run --rm provision