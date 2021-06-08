#!/bin/bash
#
#
###
# full_folder
sudo apt update
## no-input
bash <(curl -Ss https://my-netdata.io/kickstart.sh)

ansible-playbook -i hosts main.yml 

