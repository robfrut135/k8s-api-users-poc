# API users 

## Setup local env

#### Install Docker Compose

```bash
sudo curl -L "https://github.com/docker/compose/releases/download/1.27.4/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
```

#### Install Kubectl

```bash
curl -LO https://storage.googleapis.com/kubernetes-release/release/`curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt`/bin/linux/amd64/kubectl
chmod +x ./kubectl
sudo mv ./kubectl /usr/local/bin/kubectl
```

#### Install Minikube

```bash
wget https://github.com/kubernetes/minikube/releases/download/v1.14.0/minikube_1.14.0-0_amd64.deb --no-check-certificate
sudo dpkg -i minikube_1.14.0-0_amd64.deb
rm -f minikube_1.14.0-0_amd64.deb
```

#### Install VirtualBox

```bash
sudo apt install virtualbox virtualbox-ext-pack -y
```

#### Run Minikube

Run
```bash
minikube start --insecure-registry "192.168.99.0/24" --vm-driver=virtualbox
```

Enable registry
```bash
minikube addons enable registry
```

Check nodes
```bash
$ kubectl get nodes
NAME       STATUS   ROLES    AGE     VERSION
minikube   Ready    master   8m45s   v1.16.0
$
```

#### Configure Docker
Check minikube ip
```bash
$ minikube ip
192.168.99.105
$
```

Create file /etc/docker/daemon.json with this content
```bash
$ cat /etc/docker/daemon.json
{
    "insecure-registries" : [ "192.168.99.0/24" ]
}
$
```

Restart docker daemon
```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```

Check Build/Push image
```bash
docker build --tag $(minikube ip):5000/demo .
docker push $(minikube ip):5000/demo
```

Check image was uploaded correctly

```bash
$ curl $(minikube ip):5000/v2/_catalog
{"repositories":["demo"]}
$
```

## Deploy

Deployment steps

```bash
make minikube
make tests
make build
make deploy
```

Clean environment

```bash
make clean
```

## Tips
 
### Deployment pipeline

We should use a CICD tool like Jenkins, CodePipeline, Azure DevOps... to orchestrate deployment, for instance:
* run tests
* build and push docker image
* deploy new version inside dev env
* run integration tests
* promote to next environment
 
### Logging

Main steps:
* We should use a monitoring tool like CloudWatch to centralize metrics
* We should use a logging tool like CloudWatch to centralize logs
* Deploy Cloud Watch agent as Daemon Set to save metrics
* Deploy Fluentd agent as Daemon Set to collect logs inside CloudWatch 
 
### Move to production

A lot of things to do it, mainly:
* One AWS account per environment
* Use AWS EKS to manage k8s clusters
* Use your own VPC
* Enable VPC Flow logs
* Use Application Load Balancer as ingress controller to expose k8s services (API service)
* Use AWS Elasticache as cache system
* Use AWS RDS as storage system. Deploy multi-az with read replicas
* Configure backups for RDS and Elasticache
* Use ECR as private registry
* Configure ECR as registry inside AWS EKS
* Central AWS Account for CI/CD
* Jenkins (or other tool) to implement pipelines
* Cross-account permissions to enable deployment actions in environment accounts
* Proxy in front of API (envoy...)
* Implement Authentication/Authorization in API
* ...

### Reliability

* Inside K8s only deploy API, stateless service
* We have to do frequently AWS Elasticache (redis engine) backups 
* We have to enable AWS RDS backups and configure maintenance window
* Create alarms for API metrics and logs
* Create basic CloudWatch dashboard with: AWS EKS, AWS API Gateway, AWS ALB, AWS RDS, AWS Elasticache
* Identify problems/issues which we can solve by automated way (take into account metrics+logs data)
* Implement actions to solve problems/issues - triggered by alerts
* ...
