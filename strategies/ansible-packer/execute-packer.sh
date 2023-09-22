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

#? Install ARM dependencies
sudo apt-get update
sudo apt-get install -y qemu-user-static binfmt-support
sudo apt-get autoremove -y

#? Install Packer
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt-get update
sudo apt-get install -y packer

#? Create our Packer variable file
tee variables.auto.pkrvars.hcl <<PKRVARS
source_iso_sha256   = "sha256:b5e3a1d984a7eaa402a6e078d707b506b962f6804d331dcc0daa61debae3a19a"
source_iso_url      = "https://downloads.raspberrypi.org/raspios_lite_armhf/images/raspios_lite_armhf-2023-05-03/2023-05-03-raspios-bullseye-armhf-lite.img.xz"
PKRVARS

#? Run our Packer build flow
packer init .
packer validate .
sudo -E packer build .

#? Cleanup our Packer variable file
rm variables.auto.pkrvars.hcl

#? Deactivate our Python virtual environment and exit
deactivate
exit
