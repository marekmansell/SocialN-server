#!/bin/bash
app="mtaa.docker"
docker build -t ${app} .
docker run -d -p 5001:80 \
  --name=${app} \
  --env MTAA_DB_ADDR=${MTAA_DB_ADDR}
  --env MTAA_DB_PORT=${MTAA_DB_PORT}
  --env MTAA_DB_USER=${MTAA_DB_USER}
  --env MTAA_DB_PASS=${MTAA_DB_PASS}
  --env MTAA_DB_DB=${MTAA_DB_DB}
  ${app}
