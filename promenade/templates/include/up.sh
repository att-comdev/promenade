{% include "common_validation.sh" with context %}

set -e

# Ensure the script is running as root.
#
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root." 1>&2
   exit 1
fi

# Unpack prepared files into place
#
set +x
log
log === Extracting prepared files ===
echo "{{ tarball | b64enc }}" | base64 -d | tar -zxv -C /


# Set proxy variables
#
log
log === Setting proxy variables ===
set -x
export http_proxy={{ config['KubernetesNetwork:proxy.url'] | default('', true) }}
export https_proxy={{ config['KubernetesNetwork:proxy.url'] | default('', true) }}
export no_proxy={{ config.get(kind='KubernetesNetwork') | fill_no_proxy }}


# Download CNI
#
set +x
log
log === Downloading CNI binaries ===

mkdir -p /opt/cni/bin
set -x
wget -O - \
    --tries 5 \
    --retry-connrefused \
    --progress=dot:mega \
    {{ config['KubernetesNetwork:cni_tarball_url'] }} \
        | tar -zxv -C /opt/cni/bin/


# Install system packages
#
set +x
log
log === Installing system packages ===
set -x

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y --no-install-recommends \
    {%- for package in config['SystemPackages:additional'] | default([]) %}
    {{ package }} \
    {%- endfor %}
    {{ config['SystemPackages:required.docker'] }} \
    {{ config['SystemPackages:required.dnsmasq'] }} \
    {{ config['SystemPackages:required.socat'] }}


# Start core processes
#
set +x
log
log === Starting Docker and Kubelet ===
set -x
systemctl daemon-reload
systemctl restart docker || true
systemctl enable kubelet
systemctl restart kubelet


# Force resolv.conf to be injected after dnsmasq installation.
#
cat <<EOF > /etc/resolv.conf
options timeout:1 attempts:1

nameserver 127.0.0.1
{% for server in config['KubernetesNetwork:dns.upstream_servers'] | default([]) %}
nameserver {{ server }}
{%- endfor %}
EOF
