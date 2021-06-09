#!/bin/bash
#
# Sobe a aplicação, logging e monitoramento
# Pode utilizar shell ou ansible
#
###

FULL_PATH="$(realpath $0)"
FULL_FOLDER="$(dirname $FULL_PATH)"

isSwarmNode_and_existsNetwork(){
  if [[ "$(docker info | grep Swarm | sed 's/Swarm: //g' | grep inactive)" ]]; then
    echo "Iniciando swarm node"
    docker swarm init;
  else
    echo "Swarm node is active"
  fi
  if [ ! "$(docker network ls | grep paredao_backend)" ]; then
    echo "Creating paredao_backend overlay network ..."
    docker network create -d overlay --attachable paredao_backend
  else
    echo "Rede overlay OK"
  fi
}

subir_app(){
  cd $FULL_FOLDER/app && docker stack deploy -c stack.yml paredao
}

subir_logging(){
  cd $FULL_FOLDER/logging && docker stack deploy -c stack.yml logging
}

subir_monitoring(){
  cd $FULL_FOLDER/monitoramento && docker stack deploy -c stack.yml monitoring
}

full_stack_shell(){
  subir_app
  subir_logging
  subir_monitoring
}


full_stack_ansible(){
  cd $FULL_FOLDER/ansible && ansible-playbook -i hosts main.yml -v
}


if [ $(id -u) != '0'  ]; then
  echo "Execute esse comando como root"
  exit
fi

if [ $# -eq 0 ]
then
  echo "usage: $0 {subir_app|subir_logging|subir_monitoring|full_stack_shell|full_stack_ansible}"
else
  isSwarmNode_and_existsNetwork
  $1
fi
