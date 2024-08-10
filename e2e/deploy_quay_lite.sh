#!/bin/bash

SCRIPT_DIR="$(dirname "$(realpath "$BASH_SOURCE")")"
set -e

ALLOW_OPTION="--force-login"
if [[ "$1" != "$ALLOW_OPTION" ]] && jq -e '.auths["localhost:5001"]' ~/.docker/config.json > /dev/null 2>&1; then
    echo "Error: Entry for 'auths.localhost:5001' found in ~/.docker/config.json. You can use '$ALLOW_OPTION' to by-pass this check."
    exit 1
else
    echo "No entry for localhost:5001 in ~/.docker/config.json, or bypassing check with '$ALLOW_OPTION'."
fi

echo "Deploying quay K8s Secret with config.yaml ..."
FILE_NAME="config.yaml"
SECRET_NAME="quay-app-config"
cat "$SCRIPT_DIR/quay-lite/$FILE_NAME"
ENCODED_CONTENT=$(base64 -i "$SCRIPT_DIR/quay-lite/$FILE_NAME")
cat <<EOF > "$SCRIPT_DIR/quay-lite/$SECRET_NAME.yaml"
apiVersion: v1
kind: Secret
metadata:
  name: $SECRET_NAME
type: Opaque
data:
  $(basename $FILE_NAME): $ENCODED_CONTENT
EOF
cat "$SCRIPT_DIR/quay-lite/$SECRET_NAME.yaml"
kubectl apply -f "$SCRIPT_DIR/quay-lite/$SECRET_NAME.yaml"

echo "Deploying quay-lite ..."
kubectl apply -f "$SCRIPT_DIR/quay-lite/quay-all-in-one.yaml"

sleep 1
kubectl get deployments

echo "Waiting for Deployment (this will take a while)..."
kubectl wait --for=condition=available deployment/quay-app --timeout=5m
kubectl logs deployment/quay-app
echo "Deployment looks ready."

echo "Trying port-fwd until successfull (this will take a while)..."
while true; do
  echo "Starting port-forward..."
  kubectl port-forward service/quay-app 5001:5001 &
  PID=$!
  sleep 2
  echo "I have launched port-forward in background with: $PID."

  response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5001 || true) # needed because in general we have `set -e`

  if [[ $response -ge 200 && $response -lt 300 ]]; then
    echo "Service is up and running with response code: $response"
    break
  else
    echo "Waiting for service to be available. Current response code: $response"
  fi

  sleep 5
done

echo "Beginning quay admin user/initialize ..."
USER_INITALIZE=$(curl -X POST -k  http://localhost:5001/api/v1/user/initialize -H 'Content-Type: application/json' --data '{ "username": "admin", "password": "quaypass12345", "email": "quayadmin@example.com", "access_token": true}')
echo $USER_INITALIZE
TOKEN=$(echo $USER_INITALIZE | jq -r ".access_token")
echo $TOKEN
if [[ -z "$TOKEN" ]]; then
    echo "Error: Access token is null or empty."
    exit 1
fi

echo "Creating testorgns organization namespace ..."
curl -X POST -k -H 'Content-Type: application/json' -H "Authorization: Bearer $TOKEN" http://localhost:5001/api/v1/organization/ --data '{"name": "testorgns", "email": "testorgns@example.com"}'

echo "Preparing ml-model-artifact repository ..."
curl -X 'POST' \
  'http://localhost:5001/api/v1/repository' \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
  "repository": "ml-model-artifact",
  "visibility": "public",
  "namespace": "testorgns",
  "description": "string",
  "repo_kind": "image"
}'

echo "Preparing testuser quay user ..."
curl -X 'POST' \
  'http://localhost:5001/api/v1/superuser/users/' \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
  "username": "testuser",
  "email": "testuser"
}'
curl -X 'PUT' \
  'http://localhost:5001/api/v1/superuser/users/testuser' \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
  "username": "testuser",
  "email": "testuser",
  "password": "quaypass12345"
}'

echo "Granting testuser write access to testorgns/ml-model-artifact repository ..."
curl -X 'PUT' \
  'http://localhost:5001/api/v1/repository/testorgns%2Fml-model-artifact/permissions/user/testuser' \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
  "role": "write"
}'

echo "Executing oras login for testuser ..."
oras login localhost:5001 --plain-http --username testuser --password quaypass12345

echo "Current logins in ~/.docker/config.json :"
jq -r '.auths | keys[]' ~/.docker/config.json
