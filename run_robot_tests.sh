#!/bin/bash

echo "Running tests"

server_pid=""

cleanup() {
  status=$?

  if [[ -n "$server_pid" ]] && kill -0 "$server_pid" 2>/dev/null; then
    kill "$server_pid" 2>/dev/null || true
    wait "$server_pid" 2>/dev/null || true
  fi

  exit "$status"
}

trap cleanup EXIT

# luodaan tietokanta
uv run python -m src.db_helper

echo "DB setup done"

# käynnistetään Flask-palvelin taustalle
uv run python -m src.app &
server_pid=$!

echo "started Flask server"

# odetetaan, että palvelin on valmiina ottamaan vastaan pyyntöjä
server_ready=false
for _ in {1..30}; do
  if curl -fsS -o /dev/null http://localhost:5000; then
    server_ready=true
    break
  fi
  sleep 1
done

if [[ "$server_ready" != true ]]; then
  echo "Flask server did not start within 30 seconds"
  exit 1
fi

echo "Flask server is ready"

# suoritetaan testit
uv run robot --variable HEADLESS:true src/story_tests
