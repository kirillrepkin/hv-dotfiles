#!/bin/bash

function update_symlink() {
    symlink=$1
    srcfile=$2
    if [ -L "$symlink" ] && [ -e "$symlink" ]; then
        rm "$symlink"
    fi
    ln -s $srcfile $symlink
}

# libvirt hooks
update_symlink /etc/libvirt/hooks/qemu $(pwd)/libvirt/hook_qemu.sh

# modprobe
update_symlink /etc/modprobe.d/blacklist.conf $(pwd)/modprobe/blacklist.conf
update_symlink /etc/modprobe.d/vfio.conf $(pwd)/modprobe/vfio.conf

# udev rules
update_symlink /etc/udev/rules.d/99-custom-hwmon.rules $(pwd)/udev/99-custom-hwmon.rules

sudo udevadm control --reload-rules
sudo udevadm trigger