#!/usr/bin/env bash

set -eu

source "${GATE_UTILS}"

declare -a ETCD_CLUSTERS
declare -a LABELS
declare -a NODES

GET_KEYSTONE_TOKEN=0
USE_DECKHAND=0
DECKHAND_REVISION=''
OS_AUTH_URL=""
PROM_URL=""

while getopts "d:e:l:n:a:u:p:r:s:o:m:tv:" opt; do
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
        a)
            OS_AUTH_URL=${OPTARG}
            ;;
        u)
            OS_USERNAME=${OPTARG}
            ;;
        p)
            OS_PASSWORD=${OPTARG}
            ;;
        r)
            OS_PROJECT_NAME=${OPTARG}
            ;;
        s)
            OS_USER_DOMAIN_NAME=${OPTARG}
            ;;
        o)
            OS_PROJECT_DOMAIN_NAME=${OPTARG}
            ;;
        m)
            PROM_URL=${OPTARG}
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

    ARGS=""

    if [[ $GET_KEYSTONE_TOKEN == 1 ]]; then
        TOKEN="$(os_ks_get_token "${VIA}")"
        if [[ -z $TOKEN ]]; then
            log Failed to get keystone token, exiting.
            exit 1
        fi
        TOKEN_HASH=$(echo -n "${TOKEN}" | md5sum)
        log "Got keystone token, token md5sum: ${TOKEN_HASH}"
        ARGS="--token ${TOKEN}"
    elif [[ $OS_AUTH_URL ]]; then
        ARGS="--os_auth_url ${OS_AUTH_URL} --os_username ${OS_USERNAME} --os_user_domain_name ${OS_USER_DOMAIN_NAME} --os_password ${OS_PASSWORD} --os_project_name ${OS_PROJECT_NAME} --os_project_domain_name ${OS_PROJECT_DOMAIN_NAME}"
    fi

    ARGS="${ARGS} --url ${PROM_URL}"

    log "Checking Promenade API health"
    MAX_HEALTH_ATTEMPTS=6
    for attempt in $(seq ${MAX_HEALTH_ATTEMPTS}); do
        if promenade_api_health "${VIA}" "${ARGS}"; then
            log "Promenade API healthy"
            break
        elif [[ $attempt == "${MAX_HEALTH_ATTEMPTS}" ]]; then
            log "Promenade health check failed, max retries (${MAX_HEALTH_ATTEMPTS}) exceeded."
            exit 1
        fi
        sleep 10
    done

    log "Validating documents"
    promenade_api_validatedesign "${VIA}" "${REF_URL}" "${ARGS}"

    log "Fetching join script"
    JOIN_LABELS="$(render_labels "${LABELS[@]}")"
    ARGS="--hostname "${NAME}" --ip "$(config_vm_ip "${NAME}")" --design-ref "${REF_URL}" "${JOIN_LABELS}" "${ARGS}""
    promenade_api_join_scripts "${VIA}" "${ARGS}" "${NAME}"

    log "Join script received"

    log Joining node "${NAME}"
    ssh_cmd "${VIA}" "/root/promenade/join-${NAME}.sh" 2>&1 | tee -a "${LOG_FILE}"
    exit
done

sleep 10

for etcd_validation_string in "${ETCD_CLUSTERS[@]}"; do
    IFS=' ' read -a etcd_validation_args <<<"${etcd_validation_string}"
    validate_etcd_membership "${etcd_validation_args[@]}"
done
