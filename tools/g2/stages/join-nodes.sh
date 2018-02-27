#!/usr/bin/env bash

set -eu

source "${GATE_UTILS}"

declare -a ETCD_CLUSTERS
declare -a LABELS
declare -a NODES

GET_KEYSTONE_TOKEN=0
USE_DECKHAND=0

while getopts "d:e:l:n:tv:" opt; do
    case "${opt}" in
        e)
            ETCD_CLUSTERS+=("${OPTARG}")
            ;;
        d)
            USE_DECKHAND=1
            DECKHAND_REVISION=${OPTARG}
            ;;
        l)
            LABELS+=("${OPTARG}")
            ;;
        n)
            NODES+=("${OPTARG}")
            ;;
        t)
            GET_KEYSTONE_TOKEN=1
            ;;
        v)
            VIA=${OPTARG}
            ;;
        *)
            echo "Unknown option"
            exit 1
            ;;
    esac
done
shift $((OPTIND-1))

if [ $# -gt 0 ]; then
    echo "Unknown arguments specified: ${*}"
    exit 1
fi

echo Etcd Clusters: "${ETCD_CLUSTERS[@]}"
echo Labels: "${LABELS[@]}"
echo Nodes: "${NODES[@]}"

render_labels() {
    LABELS=(${@})

    LABEL_PARAMS=
    for label in "${LABELS[@]}"; do
        LABEL_PARAMS+="-dl ${label} "
    done

    echo "${LABEL_PARAMS}"
}

if [[ ${USE_DECKHAND} == 1 ]]; then
    REF_URL="deckhand%2Bhttp://deckhand-int.ucp.svc.cluster.local:9000/api/v1.0/revisions/${DECKHAND_REVISION}/rendered-documents"
else
    REF_URL="${NGINX_URL}/promenade.yaml"
fi


mkdir -p "${SCRIPT_DIR}"

for NAME in "${NODES[@]}"; do
    log Building join script for node "${NAME}"

    docker exec -i promenade /bin/bash <<'EOF'
    apt-get update
    apt-get install git
    apt-get install python3-pip
    git clone https://github.com/att-comdev/promenade.git
    cd promenade
    pip3 install -r requirements-direct.txt
    pip3 install --editable .
    export LC_ALL=C.UTF-8
    export LANG=C.UTF-8

    if [[ $GET_KEYSTONE_TOKEN == 1 ]]; then
        TOKEN="--token "
        TOKEN+="$(os_ks_get_token "${VIA}")"
        if [[ -z $TOKEN ]]; then
            log Failed to get keystone token, exiting.
            exit 1
        fi
        log "Got keystone token: ${TOKEN}"
    fi

    log "Checking Promenade API health"
    MAX_HEALTH_ATTEMPTS=6
    for attempt in $(seq ${MAX_HEALTH_ATTEMPTS}); do
        if promenade check-health; then
            log "Promenade API healthy"
            break
        elif [[ $attempt == "${MAX_HEALTH_ATTEMPTS}" ]]; then
            log "Promenade health check failed, max retries (${MAX_HEALTH_ATTEMPTS}) exceeded."
            exit 1
        fi
        sleep 10
    done

    log "Validating documents"
    promenade validatedesign --href "${REF_URL}"

    log "Fetching join script"
    JOIN_LABELS="$(render_labels)"
    promenade join-scripts --hostname "${NAME}" --ip "$(config_vm_ip "${NAME}")" --design-ref "${REF_URL}" "${JOIN_LABELS}" > "${SCRIPT_DIR}/join-${NAME}.sh"

    chmod 755 "${SCRIPT_DIR}/join-${NAME}.sh"
    log "Join script received"

    log Joining node "${NAME}"
    rsync_cmd "${SCRIPT_DIR}/join-${NAME}.sh" "${NAME}:/root/promenade/"
    ssh_cmd "${NAME}" "/root/promenade/join-${NAME}.sh" 2>&1 | tee -a "${LOG_FILE}"
    exit
    EOF
done

sleep 10

for etcd_validation_string in "${ETCD_CLUSTERS[@]}"; do
    IFS=' ' read -a etcd_validation_args <<<"${etcd_validation_string}"
    validate_etcd_membership "${etcd_validation_args[@]}"
done
