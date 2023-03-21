#!/bin/bash

SERVER_VER="c-ver1" # the version must be sync with docker compose yaml, each new code must update the version
SERVICE_NAME="crawler"
SERVER="crawler"
DOCKER_NAME="crawler"

PASSWORD="yavnun1993"

# Commands:
BUILD_ALL="build"
RUN_ALL="run"
KILL_ALL="kill"
BUILD_RUN_ALL="build-run"
LOGGING_ALL="logging"

SERVER_IMAGE_NAME="$DOCKER_NAME:"$SERVER_VER

kill_docker(){
        echo "Going to kill all running dockers of the project"
       echo $PASSWORD | sudo -S docker rm -f $SERVICE_NAME
}

build_server() {
    echo "Going to build " $SERVER " with " $SERVER_IMAGE_NAME
    docker image rm -f $SERVER_IMAGE_NAME 2> /dev/null
    docker build .. -t $SERVER_IMAGE_NAME -f Dockerfile.txt
}

build_all() {
  echo "Going to build " $BUILD_ALL
  build_server
}

run_all() {
    echo $PASSWORD | sudo -S docker-compose --project-directory .. -f ./docker-compose.yml down
    sudo docker-compose --project-directory .. -f ./docker-compose.yml --compatibility up -d
}

run_logging() {
    echo $PASSWORD | sudo -S docker logs -f $SERVICE_NAME
}

if [ "$#" -eq 1 ]; then
  if [ $1 == $BUILD_ALL ]; then
            echo "Build all images"
    build_all
  fi
  if [ $1 == $BUILD_RUN_ALL ]; then
    echo "Build & Run all images"
    kill_docker
    build_server
    run_all
  fi
  if [ $1 == $RUN_ALL ]; then
    echo "Run all images"
    run_all
  fi
  if [ $1 == $KILL_ALL ]; then
    echo "Kill all images"
    kill_docker
  fi
  if [ $1 == $LOGGING_ALL ]; then
    echo "Starting logging monitoring"
    run_logging
  fi
fi
