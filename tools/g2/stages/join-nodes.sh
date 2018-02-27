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

SCRIPT_DIR="${TEMP_DIR}/curled-scripts"
BASE_PROM_URL="http://promenade-api.ucp.svc.cluster.local"

echo Etcd Clusters: "${ETCD_CLUSTERS[@]}"
echo Labels: "${LABELS[@]}"
echo Nodes: "${NODES[@]}"


if [[ ${USE_DECKHAND} == 1 ]]; then
    DOC_URL="deckhand%2Bhttp://deckhand-int.ucp.svc.cluster.local:9000/api/v1.0/revisions/${DECKHAND_REVISION}/rendered-documents"
else
    DOC_URL="${NGINX_URL}/promenade.yaml"
fi

mkdir -p "${SCRIPT_DIR}"

for NAME in "${NODES[@]}"; do
    log Building join script for node "${NAME}"

    TOKEN="$(os_ks_get_token "${VIA}")"
    if [[ -z $TOKEN ]]; then
        log Failed to get keystone token, exiting.
        exit 1
    fi
    log "Got keystone token: ${TOKEN}"

    log "Checking Promenade API health"
    MAX_HEALTH_ATTEMPTS=6
    for attempt in $(seq ${MAX_HEALTH_ATTEMPTS}); do
        if ssh_cmd promenade check-health --token "${TOKEN}" --url "${BASE_PROM_URL}"; then
            log "Promenade API healthy"
            break
        elif [[ $attempt == "${MAX_HEALTH_ATTEMPTS}" ]]; then
            log "Promenade health check failed, max retries (${MAX_HEALTH_ATTEMPTS}) exceeded."
            exit 1
        fi
        sleep 10
    done

    log "Validating documents"
    ssh_cmd promenade validatedesign --token "${TOKEN}" --url "${BASE_PROM_URL}" --href "${DOC_URL}"

    log "Fetching join script via: ${JOIN_CURL_URL}"
    ssh_cmd promenade join-scripts --token "${TOKEN}" --url "${BASE_PROM_URL}" --hostname "${NAME}" --ip "$(config_vm_ip "${NAME}")" --design-ref "${DOC_URL}" -dl "${LABELS}" > "${SCRIPT_DIR}/join-${NAME}.sh"

    chmod 755 "${SCRIPT_DIR}/join-${NAME}.sh"
    log "Join script received"

    log Joining node "${NAME}"
    rsync_cmd "${SCRIPT_DIR}/join-${NAME}.sh" "${NAME}:/root/promenade/"
    ssh_cmd "${NAME}" "/root/promenade/join-${NAME}.sh" 2>&1 | tee -a "${LOG_FILE}"
done

sleep 10

for etcd_validation_string in "${ETCD_CLUSTERS[@]}"; do
    IFS=' ' read -a etcd_validation_args <<<"${etcd_validation_string}"
    validate_etcd_membership "${etcd_validation_args[@]}"
done
