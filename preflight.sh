#!/bin/bash
#
# Instala as dependências necessárias para rodar o projeto
#  utilizando shell ou ansible
#

FULL_PATH="$(realpath $0)"
FULL_FOLDER="$(dirname $FULL_PATH)"


basic() {
  sudo apt update
  sudo apt install python3-pip -y
  # sudo timedatectl set-timezone America/Sao_Paulo
  # para fazer o download dos dados de logging
  pip install gdown
}

shell(){
  basic
  if [[ $(command -v docker) == "" ]]; then
    curl -sS https://get.docker.com | bash
  fi

}

ansible(){
  basic
  sudo apt install python3-pip ansible -y
  pip install docker
  echo "  app_dir: \"$FULL_FOLDER\"" >> $FULL_FOLDER/ansible/group_vars/all
}


if [ $# -eq 0 ]
then
  echo "usage: $0 {shell|ansible}"
else
  $1
fi
