#!/usr/bin/env bash

#? Brush the dust off apt-get
sudo apt-get update
sudo apt-get upgrade -y --no-install-recommends
sudo apt-get install -y -f

#? Copy the overlay files to the boot partition
sudo cp -R ./bootfs/* /

#? The userconf.txt file is used by RPiOS to configure
#? an initial user on first boot
PW_HASH=$(openssl passwd -1 raspberry)
sed -i "s!^dmp:.*$!dmp:${PW_HASH}!" /boot/userconf.txt

#? If the locale isn't already configured, do it now
if [[ ("$LC_ALL" != "en_US.UTF-8") || ("$LANGUAGE" != "en_US.UTF-8") ]]; then
  sed -i 's@^# en_US.UTF-8 UTF-8$@en_US.UTF-8 UTF-8@g' /etc/locale.gen
  sed -i 's@en_GB.UTF-8 UTF-8$@^# en_GB.UTF-8 UTF-8@g' /etc/locale.gen
  locale-gen
  update-locale LANGUAGE=en_US.UTF-8 LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
fi

sudo apt-get update
xargs sudo apt-get install -y </usr/local/share/apt/gui.depends
sudo apt-get install -y -f
xargs sudo apt-get install -y </usr/local/share/apt/hardware.depends
sudo apt-get install -y -f
xargs sudo apt-get install -y </usr/local/share/apt/audio.depends
sudo apt-get install -y -f
