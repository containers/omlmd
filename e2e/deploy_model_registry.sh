ca#!/bin/bash

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
kubectl apply -k "https://github.com/kubeflow/model-registry/manifests/kustomize/overlays/db?ref=v0.2.4-alpha"

sleep 1
kubectl get -n kubeflow deployments

echo "Waiting for Deployment..."
kubectl wait --for=condition=available -n kubeflow deployment/model-registry-deployment --timeout=1m
kubectl logs -n kubeflow deployment/model-registry-deployment
echo "Deployment looks ready."

echo "Starting port-forward..."
kubectl port-forward svc/model-registry-service -n kubeflow 8081:8080 &
PID=$!
sleep 2
echo "I have launched port-forward in background with: $PID."
