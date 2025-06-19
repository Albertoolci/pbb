#!/bin/bash
az aks create \
  --resource-group pbb \
  --name pbb \
  --node-count 2 \
  --network-plugin azure \
  --network-policy calico \
  --enable-managed-identity \
  --enable-asm \
  --node-vm-size Standard_B2ms \
  --generate-ssh-keys



az aks get-credentials --resource-group pbb --name pbb
kubectl apply -f templates/istio/strict-mtls-global.yaml
kubectl create secret generic mysql-root-secret \
  --from-literal=root-password=$(openssl rand -base64 48 | tr -dc 'a-zA-Z0-9' | head -c 32)
kubectl create secret generic mysql-inserter-secret \
  --from-literal=inserter-password=$(openssl rand -base64 48 | tr -dc 'a-zA-Z0-9' | head -c 32)
kubectl create secret generic mysql-web-secret \
  --from-literal=web-password=$(openssl rand -base64 48 | tr -dc 'a-zA-Z0-9' | head -c 32)
kubectl create secret generic inserter-key-cert \
  --from-file=inserter.crt=./inserter.crt \
  --from-file=inserter.key=./inserter.key \
  --namespace=default
kubectl create secret generic client-cert \
  --from-file=client.crt.pem=./client.crt.pem \
  --namespace=default
kubectl create secret tls web-tls-secret \
  --cert=./templates/web/ssl/web.cert.pem \
  --key=./templates/web/ssl/web.key.pem \
  --namespace=default
kubectl create secret tls gateway-tls \
  --cert=./gateway.crt.pem \
  --key=./gateway.key.pem \
  --namespace=default

az network public-ip create --resource-group MC_pbb_pbb_westeurope --name pbb --sku Standard --allocation-method static
az aks get-credentials --resource-group pbb --name pbb
kubectl get pods -n aks-istio-system
az aks show --resource-group pbb --name pbb --query 'serviceMeshProfile.mode'

az aks mesh enable-ingress-gateway \
  --resource-group pbb \
  --name pbb \
  --ingress-gateway-type External

kubectl create secret tls gateway-tls \
    --cert=./gateway.crt.pem \
    --key=./gateway.key.pem \
    --namespace=aks-istio-ingress






