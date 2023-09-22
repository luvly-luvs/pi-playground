#!/usr/bin/env bash
# shellcheck source=/dev/null

#? Make sure we have Python installed and up-to-date
if ! command -v python3 &>/dev/null; then
  sudo apt-get update
  sudo apt-get install -y -f python3 python3-pip python3-venv
  sudo apt-get autoremove -y
fi

#? Start our Python virtual environment
[[ ! -d ".venv" ]] && python3 -m venv .venv
source .venv/bin/activate

#? Install Python requirements
pip3 install --upgrade pip
pip3 install --upgrade setuptools wheel
pip3 install "ansible >= 2.3" passlib

#? Execute our Ansible playbook
ansible-playbook bootstrap.playbook.yml

#? Deactivate our Python virtual environment and exit
deactivate
exit
