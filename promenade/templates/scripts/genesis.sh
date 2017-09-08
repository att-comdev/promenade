{% include "up.sh" with context %}

set +x
log
log === Waiting for Kubernetes API availablity ===
set -x
wait_for_kubernetes_api 3600

set +x
log
log === Deploying bootstrap manifest via Armada ===
set -x

while true; do
    sleep 10
    if armada apply --debug /etc/kubernetes/armada/assets/manifest.yaml ; then
        break
    fi
done

set +x
log
log === Waiting for Node to be Ready ===
set -x
wait_for_ready_nodes 1 3600

set +x
log
log === Finished genesis process ===
