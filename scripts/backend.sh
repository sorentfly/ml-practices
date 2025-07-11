#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && cd .. && pwd )"
DOCKERFILE="Dockerfile"
ARCH=$(uname -m)

if [[ "$ARCH" == "arm64" ]]; then
#   DOCKERFILE="Dockerfile-arm64v8"
    echo "Not implemented yet"
    exit
fi

case "$1" in
  --install)
    docker build -f "$DIR/docker/$DOCKERFILE" -t smith/python3.12/ai "$DIR"
    docker compose -f "$DIR/docker/docker-compose.yml" up -d
    # docker compose exec smith-ai python /opt/app/main.py
    ;;
  --reinstall)
    docker compose down -v
    ./backend.sh --install
    ;;
  *)
    docker compose up -d
    ;;
esac

# shellcheck disable=SC2164
cd "$DIR"