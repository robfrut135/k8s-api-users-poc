API_DOMAIN ?= $(shell minikube ip)
API_DOMAIN ?=
REGISTRY ?= $(shell minikube ip):5000
DOCKER_IMAGE = $(REGISTRY)/demo
VERSION ?= latest

.PHONY: default minikube build deploy tests

default:
	echo "Set one action"

minikube:
	minikube delete
	minikube start --insecure-registry "192.168.99.0/24"
	minikube addons enable registry
	kubectl get nodes

clean:
	minikube delete
	docker-compose stop
	docker-compose rm -f

build:
	echo version=$(VERSION)
	docker build --tag $(DOCKER_IMAGE) .
	docker push $(DOCKER_IMAGE)
ifneq ($(VERSION), latest)
	docker build --tag $(DOCKER_IMAGE):$(VERSION) .
	docker push $(DOCKER_IMAGE):$(VERSION)
endif
	curl $(REGISTRY)/v2/_catalog
	curl $(REGISTRY)/v2/demo/tags/list

deploy:
	kubectl -n demo apply -f k8s/ns.yml
	kubectl -n demo apply -f k8s/db.yml
	DOCKER_IMAGE=$(DOCKER_IMAGE) envsubst < k8s/api.yml | kubectl -n demo apply -f -
	sleep 20
	kubectl -n demo get pods
	sleep 40
	curl $(API_DOMAIN):8888/users/health

tests:
	docker-compose up --build -d
	tox
	docker-compose stop
	docker-compose rm -f

docker:
	docker-compose up --build -d
