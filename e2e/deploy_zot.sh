#!/bin/bash

SCRIPT_DIR="$(dirname "$(realpath "$BASH_SOURCE")")"
set -e

helm repo add zot https://zotregistry.dev/helm-charts/

# Notes:
# - if used manually in local testing, might want to change to `upgrade` or `helm uninstall my-zot` first,
# - the custom values contains tag image which is Arch-specific, might want to replace amd64 -> arm64 if needed for local testing
helm install my-zot zot/zot --version 0.1.58 -f "${SCRIPT_DIR}/zot/custom-values.yaml"

sleep 1
kubectl get deployments

echo "Waiting for Deployment..."
kubectl wait --for=condition=available deployment/my-zot --timeout=5m
kubectl logs deployment/my-zot
echo "Deployment looks ready."

echo "Starting port-forward..."
kubectl port-forward service/my-zot 5001:5001 &
PID=$!
sleep 2
echo "I have launched port-forward in background with: $PID."
