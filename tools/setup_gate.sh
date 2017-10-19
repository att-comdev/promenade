#!/usr/bin/env bash

set -e

SCRIPT_DIR=$(realpath $(dirname $0))

C_CLEAR="\e[0m"
C_ERROR="\e[38;5;160m"
C_HEADER="\e[38;5;164m"
C_HILIGHT="\e[38;5;27m"
C_SUCCESS="\e[38;5;46m"

REQUIRE_REBOOT=0
REQUIRE_RELOG=0

echo -e ${C_HEADER}=== Installing Packages ===${C_CLEAR}
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -qq
sudo apt-get install -q -y --no-install-recommends \
    curl \
    docker.io \
    genisoimage \
    jq \
    libvirt-bin \
    virtinst

echo -e ${C_HEADER}=== Joining User Groups ===${C_CLEAR}
for grp in docker libvirtd; do
    if ! groups | grep $grp > /dev/null; then
        sudo adduser `id -un` $grp
        REQUIRE_RELOG=1
    fi
done

echo -e ${C_HEADER}=== Setting Kernel Parameters ===${C_CLEAR}
if [ "xY" != "x$(cat /sys/module/kvm_intel/parameters/nested)" ]; then
    echo -e {$C_HILIGHT}NOTE:${C_CLEAR} Enabling nested virtualization.
    sudo modprobe -r kvm_intel
    sudo modprobe kvm_intel nested=1
    echo "options kvm-intel nested=1" | sudo tee /etc/modprobe.d/kvm-intel.conf
fi

if ! sudo virt-host-validate qemu &> /dev/null; then
    if ! grep intel_iommu /etc/defaults/grub &> /dev/null; then
        echo -e {$C_HILIGHT}NOTE:${C_CLEAR} Enabling Intel IOMMU
        REQUIRE_REBOOT=1
        sudo mkdir -p /etc/defaults
        sudo touch /etc/defaults/grub
        echo 'GRUB_CMDLINE_LINUX_DEFAULT="${GRUB_CMDLINE_LINUX_DEFAULT} intel_iommu=on"' | sudo tee -a /etc/defaults/grub
    else
        echo -e ${C_ERROR}Failed to configure virtualization:${C_CLEAR}
        sudo virt-host-health qemu
        exit 1
    fi
fi

if [ $REQUIRE_REBOOT -eq 1 ]; then
    echo
    echo -e ${C_HILIGHT}NOTE:${C_CLEAR} You must ${C_HEADER}reboot${C_CLEAR} before for the gate is ready to run.
elif [ $REQUIRE_RELOG -eq 1 ]; then
    echo
    echo -e ${C_HILIGHT}NOTE:${C_CLEAR} You must ${C_HEADER}log out${C_CLEAR} and back in before the gate is ready to run.
fi
echo -e ${C_SUCCESS}=== Done ===${C_CLEAR}
