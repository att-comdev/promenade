set +x
log
log === Removing temporary NAT rules for Kubernetes service ===
set -x
set +e
iptables -t nat -D OUTPUT $(iptables -nL OUTPUT -t nat --line-numbers | grep PROMENADE_CLEANUP | awk '{print $1}')
iptables -t nat -D POSTROUTING $(iptables -nL POSTROUTING -t nat --line-numbers | grep PROMENADE_CLEANUP | awk '{print $1}')
set -e

set +x
log
log === Restarting kubelet ===
set -x
systemctl restart kubelet
