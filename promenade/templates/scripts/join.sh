{% include "header.sh" %}

set +x
log
log === Creating Temporary NAT rules for Kubernetes service ===
set -x
iptables -t nat -A OUTPUT \
    -m comment --comment PROMENADE_CLEANUP \
    -d {{ config['KubernetesNetwork:kubernetes.service_ip'] }} \
    -j DNAT --to-destination {{ config['KubernetesNode:join_ip'] }}
iptables -t nat -A POSTROUTING \
    -m comment --comment PROMENADE_CLEANUP \
    -j MASQUERADE

{% include "up.sh" with context %}

set +x
log
log === Waiting for Node to be Ready ===
set -x
wait_for_node_ready {{ config.get_first('Genesis:hostname', 'KubernetesNode:hostname') }} 3600

{%- if config['KubernetesNode:labels.dynamic']  is defined %}
set +x
log
log === Registering dynamic labels for node ===
set -x
register_labels {{ config['KubernetesNode:hostname'] }} 3600 {{ config['KubernetesNode:labels.dynamic'] | join(' ') }}
{%- endif %}

sleep 60

{% include "cleanup.sh" with context %}

set +x
log
log === Finished join process ===
