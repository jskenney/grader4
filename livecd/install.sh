#!/bin/bash

#https://stackoverflow.com/questions/30248794/run-docker-in-ubuntu-live-disk
#https://askubuntu.com/questions/1361135/editing-the-ubuntu-iso-to-skip-try-install-page-with-cubic
#https://askubuntu.com/questions/1361056/editing-ubuntu-iso-with-cubic-to-skip-the-disk-check
#https://askubuntu.com/questions/1344336/cubic-custom-iso-which-executes-shell-script-at-startup/1344607#1344607

# Install Software in Cubic
apt update
apt dist-upgrade -y
apt install -y docker.io git curl

# Purge Ubuntu installers in the graphical environment
apt autoremove --purge ubiquity ubiquity-casper ubiquity-frontend-gtk ubiquity-slideshow-ubuntu ubiquity-ubuntu-artwork
apt install -y open-vm-tools open-vm-tools-desktop

apt purge -y language-pack-gnome-es-base language-pack-gnome-pt-base language-pack-es-base language-pack-pt-base language-pack-gnome-zh-hans-base gnomine gnome-sudoku language-pack-gnome-xh-base language-pack-gnome-xh language-pack-zh-hans-base ttf-wqy-microhei ttf-punjabi-fonts shotwell simple-scan empathy empathy-common evolution-common gucharmap pitivi banshee language-pack-gnome-de-base
apt purge -y liblouis-data foo2zjs cmap-adobe-japan1 brltty pinyin* thunderbird language-pack-gnome-fr-base gnumeric* gimp* pidgin* xchat* orage* aisleriot mahjongg brasero brasero-common leafpad onboard gnome-mines transmission-gtk gnome-mahjongg cheese rhythmbox*
apt purge -y deja-dup zeitgeist-core vino remmina


# Edit /etc/groups and add (check what the gid is first)
echo 'docker:x:122:ladmin,ubuntu,ubuntu-mate,ubuntu-server' | tee -a /etc/group
echo 'docker:x:122:ladmin,ubuntu,ubuntu-mate,ubuntu-server' | tee -a /etc/group-
echo 'docker:!::ladmin,ubuntu,ubuntu-mate,ubuntu-server' | tee -a /etc/gshadow
echo 'docker:!::ladmin,ubuntu,ubuntu-mate,ubuntu-server' | tee -a /etc/gshadow-

# Fix USNA certificates
curl apt.cs.usna.edu/ssl/install-ssl-system.sh | bash

# For USNA intranet
echo """{
   \"dns\": [\"10.1.74.10\"],
   \"storage-driver\": \"devicemapper\"
} """ | tee /etc/docker/daemon.json

# Clone graderv4
pushd /opt
git clone https://gitlab.usna.edu/webdev/grader-v4.git
chown -R 1000:1000 grader-v4
popd

#

pushd /tmp/grader-v4/cs-base
docker build -t cs-base .
popd

# For internal VM Network
#echo """{
#    \"dns\": [\"192.168.0.1\"],
#    \"storage-driver\": \"devicemapper\"
#} """ | tee configs/192.168/etc/docker/daemon.json

# For USNA intranet
#echo """{
#    \"dns\": [\"10.1.74.10\"],
#    \"storage-driver\": \"devicemapper\"
#} """ | tee configs/10.1/etc/docker/daemon.json

# Step to copy contents of config/xxx.xxx directory based on ip address range

# Restart docker
sudo service docker restart
