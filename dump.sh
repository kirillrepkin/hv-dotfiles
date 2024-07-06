#!/bin/bash
url=$1

if [[ $url == "" ]]; then
    echo Error: connection url should be passed as first argument.
    exit 1
fi

mkdir -p libvirt/domains
domain_list=$(virsh --connect=${url} list --all | grep '-' | awk '{ print $2 }' )
for domain in $domain_list; do
    if [[ $domain != "" ]]; then
        echo dumping $domain
        rm libvirt/domains/$domain.xml
        virsh --connect=${url} dumpxml $domain > libvirt/domains/$domain.xml
    fi
done