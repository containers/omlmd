#!/bin/bash

SCRIPT_DIR="$(dirname "$(realpath "$BASH_SOURCE")")"
set -e

if [[ "$OSTYPE" == "darwin"* ]]; then
  # Mac OSX
  echo "Error: As Kubeflow Model Registry wraps Google's MLMD and no source image for Mchips, this deployment is not supported. Using a temp docker-compose."
  rm "$SCRIPT_DIR/model-registry/config/ml-metadata/metadata.sqlite.db" || true
  docker compose -f "$SCRIPT_DIR/model-registry/docker-compose.yaml" up
  exit 0
fi

kubectl create namespace kubeflow
kubectl apply -n kubeflow -k "https://github.com/kubeflow/model-registry/manifests/kustomize/overlays/db?ref=v0.2.20"

sleep 1
kubectl get -n kubeflow deployments

echo "Waiting for Deployments..."

echo "Waiting for Model Registry DB deployment..."
if ! kubectl wait --for=condition=available -n kubeflow deployment/model-registry-db --timeout=2m; then
  kubectl get -n kubeflow deployments
  kubectl events -A
  kubectl describe deployment/model-registry-db -n kubeflow
  kubectl logs deployment/model-registry-db -n kubeflow
  exit 1
fi
echo "Model Registry DB deployment is ready."

echo "=== Model Registry DB Logs ==="
kubectl logs -n kubeflow deployment/model-registry-db

echo "Waiting for Model Registry deployment..."
if ! kubectl wait --for=condition=available -n kubeflow deployment/model-registry-deployment --timeout=1m; then
  echo "Model Registry deployment failed or timed out."
  kubectl get -n kubeflow deployments
  echo "=== Model Registry Deployment Logs ==="
  kubectl logs -n kubeflow deployment/model-registry-deployment
  exit 1
fi
echo "Model Registry deployment is ready."

echo "=== Model Registry Deployment Logs ==="
kubectl logs -n kubeflow deployment/model-registry-deployment
echo "Deployments status checked."

echo "Starting port-forward..."
kubectl port-forward svc/model-registry-service -n kubeflow 8081:8080 &
PID=$!
sleep 2
echo "I have launched port-forward in background with: $PID."
