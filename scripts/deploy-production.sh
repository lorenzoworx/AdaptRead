#!/usr/bin/env bash
set -Eeuo pipefail

: "${GITHUB_SHA:?GITHUB_SHA is required}"
: "${GITHUB_RUN_ID:?GITHUB_RUN_ID is required}"
: "${DEPLOY_STACK_DIR:?DEPLOY_STACK_DIR is required}"
: "${PRODUCTION_URL:?PRODUCTION_URL is required}"

short_sha=${GITHUB_SHA:0:12}
release_image="personal-web-adaptread:release-${short_sha}"
production_image="personal-web-adaptread:1"
rollback_image="personal-web-adaptread:rollback-before-${short_sha}"
candidate_container="adaptread-candidate-${GITHUB_RUN_ID}"
compose_file="${DEPLOY_STACK_DIR}/compose.yml"
promoted=0

cleanup() {
  status=$?
  set +e
  docker container rm --force "$candidate_container" >/dev/null 2>&1
  if [[ $status -ne 0 && $promoted -eq 1 ]]; then
    echo "Deployment failed after promotion; restoring ${rollback_image}." >&2
    docker image tag "$rollback_image" "$production_image"
    docker compose -f "$compose_file" up -d --no-deps --force-recreate --wait adaptread
  fi
  exit "$status"
}
trap cleanup EXIT

test -f "$compose_file"
docker image inspect "$production_image" >/dev/null
docker image tag "$production_image" "$rollback_image"

docker build \
  --label "org.opencontainers.image.revision=${GITHUB_SHA}" \
  --tag "$release_image" \
  .

docker run --detach \
  --name "$candidate_container" \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=16m,uid=10001,gid=10001 \
  --user 10001:10001 \
  --cap-drop ALL \
  --security-opt no-new-privileges \
  "$release_image" >/dev/null

for attempt in {1..45}; do
  if docker exec "$candidate_container" python -c \
      "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz')"; then
    break
  fi
  if [[ $attempt -eq 45 ]]; then
    docker logs "$candidate_container"
    exit 1
  fi
  sleep 2
done
docker exec "$candidate_container" python -c \
  "import json, urllib.request; request=urllib.request.Request('http://127.0.0.1:8000/v1/sessions', data=b'{}', headers={'Content-Type':'application/json'}); response=json.load(urllib.request.urlopen(request)); assert response['simulated_only'] is True"

docker container rm --force "$candidate_container" >/dev/null
docker image tag "$release_image" "$production_image"
promoted=1
docker compose -f "$compose_file" up -d --no-deps --force-recreate --wait adaptread

deployed_revision=$(docker inspect personal-web-adaptread-1 --format '{{ index .Config.Labels "org.opencontainers.image.revision" }}')
test "$deployed_revision" = "$GITHUB_SHA"
python3 scripts/smoke_deployment.py "${PRODUCTION_URL%/}/projects/adaptread"

promoted=0
echo "AdaptRead ${GITHUB_SHA} is live; rollback image: ${rollback_image}."
