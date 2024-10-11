#!/bin/bash

git fetch origin
reslog=$(git log HEAD..origin/main --oneline)
if [[ "${reslog}" != "" ]]; then
  git merge origin/main
  docker compose build
  docker compose down -v
  docker compose up -d
  echo "Updated local repo"
else
  echo "Local repo up to date"
fi
