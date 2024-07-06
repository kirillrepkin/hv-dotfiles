#!/bin/bash

function update_symlink() {
    symlink=$1
    srcfile=$2
    if [ -f "$symlink" ]; then
        rm "$symlink"
    fi
    ln -s $symlink $srcfile
}

update_symlink /etc/libvirt/hooks/qemu $(pwd)/libvirt_hook_qemu.sh
