#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && cd .. && pwd )"

case "$1" in
  --install)
    docker build -f "$DIR/docker/Dockerfile" -t smith/python3.12/ai "$DIR"
    docker compose -f "$DIR/docker/docker-compose.yml" up -d
    ;;
  --reinstall)
    docker compose -f "$DIR/docker/docker-compose.yml" down -v
    ./backend.sh --install
    ;;
  *)
    docker compose -f "$DIR/docker/docker-compose.yml" up -d
    ;;
esac

cd "$DIR"