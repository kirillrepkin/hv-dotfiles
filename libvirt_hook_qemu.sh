#!/bin/bash
command=$2
guest_name=$1
tmp_file=/tmp/libvirt_guest_name.txt


# Resets a USB device by finding the device with the specified vendor ID and product ID and then toggling its authorization.
# 
#   VENDOR (str): The vendor ID of the USB device.
#   PRODUCT (str): The product ID of the USB device.
function usb_reset() {
	VENDOR=$1
	PRODUCT=$2
	for DIR in $(find /sys/bus/usb/devices/ -maxdepth 1 -type l); do
	if [[ -f $DIR/idVendor && -f $DIR/idProduct &&
			$(cat $DIR/idVendor) == $VENDOR && $(cat $DIR/idProduct) == $PRODUCT ]]; then
		echo 0 > $DIR/authorized
		sleep 0.5
		echo 1 > $DIR/authorized
	fi
	done
}

# Removes port forwarding rules for a specific guest IP, guest port, and host port using iptables.
#
# @param GUEST_IP The IP address of the guest machine.
# @param GUEST_PORT The port number on the guest machine.
# @param HOST_PORT The port number on the host machine.
function add_port_nat_port_forwarding() {
	GUEST_IP=$1
	GUEST_PORT=$2
	HOST_PORT=$3
	iptables -I FORWARD -o virbr0 -p tcp -d $GUEST_IP --dport $GUEST_PORT -j ACCEPT
	iptables -t nat -I PREROUTING -p tcp --dport $HOST_PORT -j DNAT --to $GUEST_IP:$GUEST_PORT
}

# Removes port forwarding rules for a specific guest IP, guest port, and host port using iptables.
#
# @param GUEST_IP The IP address of the guest machine.
# @param GUEST_PORT The port number on the guest machine.
# @param HOST_PORT The port number on the host machine.
# @return void
function remove_port_nat_port_forwarding() {
	GUEST_IP=$1
	GUEST_PORT=$2
	HOST_PORT=$3
	iptables -D FORWARD -o virbr0 -p tcp -d $GUEST_IP --dport $GUEST_PORT -j ACCEPT
	iptables -t nat -D PREROUTING -p tcp --dport $HOST_PORT -j DNAT --to $GUEST_IP:$GUEST_PORT
}

# Sets the CPU cores that can be used by the system, user, and init.scope slices.
#
# @param CORES A string of comma-separated CPU core numbers.
# @return void
function cpu_cores_borrowing() {
	CORES=$1
	systemctl set-property --runtime -- system.slice AllowedCPUs=${CORES}
	systemctl set-property --runtime -- user.slice AllowedCPUs=${CORES}
	systemctl set-property --runtime -- init.scope AllowedCPUs=${CORES}
}

# Manipulates the GUI of the application based on the command received.
function app_gui_manipulation() {
	if [[ $command == "started" ]]; then
		echo $guest_name | tee $tmp_file
	elif [[ $command == "release" ]]; then
		rm $tmp_file
	fi
}

# Manipulates the CPU cores that can be used by the system, user, and init.scope slices based on the command received.
function app_cpu_manipulation() {
	if [[ $command == "started" ]]; then
		cpu_cores_borrowing "0,8,1,9,2,10,3,11"
	elif [[ $command == "release" ]]; then
		cpu_cores_borrowing "0-15"
	fi
}

# Manipulates the USB device with the specified vendor ID and product ID based on the command received.
function app_usb_manipulation() {
    if [[ $command == "started" ]]; then
        usb_reset 8087 0aaa
    elif [[ $command == "release" ]]; then
        usb_reset 8087 0aaa
    fi
}

function get_domain_ipv4_addr() {
	echo $(virsh domifaddr $1 | grep ipv4 | awk '{print $4}' | cut -d'/' -f1)
}

# Manipulates network settings based on the command received.
function app_network_manipulation() {
	if [[ $command == "stopped" ]] || [[ $command == "reconnect" ]]; then
		ipv4_addr=get_domain_ipv4_addr $guest_name
		if [[ $guest_name == "windows" ]]; then
			# sunshine/moonlight remote gaming
			remove_port_nat_port_forwarding $ipv4_addr 13333 13333 
		fi
	fi
	if [[ $command == "started" ]] || [[ $command == "reconnect" ]]; then
		ipv4_addr=get_domain_ipv4_addr $guest_name
		if [[ $guest_name == "windows" ]]; then
			# sunshine/moonlight remote gaming
			add_port_nat_port_forwarding $ipv4_addr 13333 13333
		fi
	fi	
}

# Manages the application based on the command received.
function libvirt_qemu_hook() {
	app_usb_manipulation
	app_gui_manipulation
	app_cpu_manipulation
	app_network_manipulation
}

# run libvirt hook
libvirt_qemu_hook