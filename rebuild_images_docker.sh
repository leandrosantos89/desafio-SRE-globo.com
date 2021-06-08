#!/bin/bash

FULL_PATH="$(realpath $0)"
FULL_FOLDER="$(dirname $FULL_PATH)"

api(){
  cd $FULL_FOLDER/app/api && docker build -t paredao-api .
}
consumer(){
  cd $FULL_FOLDER/app/consumer && docker build -t paredao-consumer .
}
proxy(){
  cd $FULL_FOLDER/app/proxy && docker build -t nginx-ubuntu .
}
graylog-colllector(){
  cd $FULL_FOLDER/logging && docker build -t graylog-collector -f Dockerfile-graylog-collector .
}

all(){
  consumer
  proxy
  api
  graylog-colllector
}

fake(){
  echo 'teste'
}

if [ $# -eq 0 ]
then
  echo "usage: $0 {api|consumer|proxy|graylog-collector|all}"
else
  $1
fi

