{% include "header.sh" with context %}

for node in $(kubectl get nodes -o name); do
    validate_kubectl_logs $node
done
