#!/bin/bash
#
#

# deixar tudo como localhost
## chamadas de api do javascript

FULL_PATH="$(realpath $0)"
FULL_FOLDER="$(dirname $FULL_PATH)"


sudo apt update
sudo apt install python3-pip ansible
pip install docker



echo "  app_dir: \"$FULL_FOLDER\"" >> $FULL_FOLDER/ansible/group_vars/all

#sudo timedatectl set-timezone America/Sao_Paulo
