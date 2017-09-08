{% include "utils.sh" with context %}

# Disable overwriting our resolv.conf
#
resolvconf --disable-updates

# Unpack prepared files into place
#
set +x
log
log === Extracting prepared files ===
echo "{{ tarball | b64enc }}" | base64 -d | tar -zxv -C / | tee /etc/promenade-manifest

# Adding apt repositories
#
set +x
log
log === Adding APT Keys===
set -x
{%- for key in config.get_path('SystemPackages:keys', []) %}
apt-key add - <<"ENDKEY"
{{ key }}
ENDKEY
{%- endfor %}

# Disable swap
#
set +x
log
log === Disabling swap ===
set -x
swapoff -a
sed --in-place '/\bswap\b/d' /etc/fstab

# Set proxy variables
#
set +x
log
log === Setting proxy variables ===
set -x
export http_proxy={{ config['KubernetesNetwork:proxy.url'] | default('', true) }}
export https_proxy={{ config['KubernetesNetwork:proxy.url'] | default('', true) }}
export no_proxy={{ config.get(kind='KubernetesNetwork') | fill_no_proxy }}


# Install system packages
#
set +x
log
log === Installing system packages ===
set -x

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y --no-install-recommends \
    {%- for package in config['SystemPackages:packages.additional'] | default([]) %}
    {{ package }} \
    {%- endfor %}
    {{ config['SystemPackages:packages.required.docker'] }} \
    {{ config['SystemPackages:packages.required.ipset'] }} \
    {{ config['SystemPackages:packages.required.socat'] }}


# Start core processes
#
set +x
log
log === Starting Docker and Kubelet ===
set -x
systemctl daemon-reload
systemctl restart docker || true
systemctl enable iptables-loader
systemctl enable kubelet
systemctl restart kubelet
