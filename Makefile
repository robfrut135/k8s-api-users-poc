API_DOMAIN ?= $(shell minikube ip)
REGISTRY ?= $(shell minikube ip):5000
DOCKER_IMAGE = $(REGISTRY)/api-users
VERSION ?= latest
NAMESPACE = api-users

.PHONY: default minikube build deploy tests

default:
	echo "Set one action"

minikube:
	minikube delete
	minikube start --insecure-registry "192.168.99.0/24" --vm-driver=virtualbox
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
	curl $(REGISTRY)/v2/api-users/tags/list

deploy:
	NAMESPACE=$(NAMESPACE) envsubst < k8s/ns.yml | kubectl apply -f -
	kubectl -n $(NAMESPACE) apply -f k8s/db.yml
	sleep 5
	DOCKER_IMAGE=$(DOCKER_IMAGE) envsubst < k8s/api.yml | kubectl -n $(NAMESPACE) apply -f -
	sleep 30
	kubectl -n $(NAMESPACE) get pods
	sleep 40
	curl $(API_DOMAIN):$(shell kubectl -n $(NAMESPACE) get svc api --output='jsonpath="{.spec.ports[0].nodePort}"' | sed s/\"//g)/users/health

tests:
	docker-compose up --build -d
	tox
	docker-compose stop
	docker-compose rm -f

docker:
	docker-compose up --build -d
