#!/bin/bash
app="active-fc"
docker build -t ${app} .
docker run -d -p 5005:5005 \
  --name=${app} \
  -v $PWD:/app ${app}
