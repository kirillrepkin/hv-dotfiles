# Hypervisor Dotfiles

This repository contains configuration files for the Hypervisor (or `hv` for short).

## Installation

To install you can use the following command:

```sh
sudo ./install.sh
```

## Dumping domains

```sh
./dump.sh qemu+ssh://hv/system
```

## CPU pinning

```sh
python3 ./src/cpupingen.py --total-cores 16 --threads-per-core 2 --io-threads 4 --system-cores 0,1,2,3 --virtual-cores 12
```

```xml
<systemcpulayout>
        <cpu mode='host-passthrough' check='none' migratable='on'>
                <topology sockets='1' dies='1' clusters='1' cores='4' threads='2'/>
        </cpu>
        <iothreads>2</iothreads>
        <cputune>
                <vcpupin vcpu='0' cpuset='4'/>
                <vcpupin vcpu='1' cpuset='5'/>
                <vcpupin vcpu='2' cpuset='6'/>
                <vcpupin vcpu='3' cpuset='7'/>
                <vcpupin vcpu='4' cpuset='8'/>
                <vcpupin vcpu='5' cpuset='9'/>
                <vcpupin vcpu='6' cpuset='10'/>
                <vcpupin vcpu='7' cpuset='11'/>
                <emulatorpin cpuset='0,1,2,3'/>
                <iothreadpin iothread='1' cpuset='0,1,2,3'/>
                <iothreadpin iothread='2' cpuset='0,1,2,3'/>
        </cputune>
</systemcpulayout>
```

## VM xml modyfing

```sh
# default script execution
python3 ./src/modifyvm.py --domain windows@hv --layout dual_half_left

# override memory value defined in layout file
python3 ./src/modifyvm.py --domain windows@hv --layout dual_half_left --memory 16

# dry run mode (without saving modifications)
python3 ./src/modifyvm.py --domain windows@hv --layout dual_half_left --memory 16 --dry-run Y
```