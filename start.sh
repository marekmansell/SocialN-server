#!/bin/bash
app="mtaa.docker"
docker build -t ${app} .
docker run -d -p 5001:80 \
  --name=${app} \
  -v $PWD:/app ${app}
