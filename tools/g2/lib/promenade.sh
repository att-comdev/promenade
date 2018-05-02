IMAGE_PROMENADE=${IMAGE_PROMENADE:-quay.io/attcomdev/promenade:latest}
SCRIPT_DIR=$(realpath $(dirname $0))
BUILD_DIR=$(realpath ${2:-${SCRIPT_DIR}/../build})

promenade_api_health() {
    NAME=${1}
    ARGS=${2}

    ssh_cmd "${NAME}"
    docker run --rm -t -w /target -v ${BUILD_DIR}:/target \
        ${IMAGE_PROMENADE} promenade check-health "${ARGS}"
}

promenade_api_validatedesign() {
    NAME=${1}
    REF_URL=${2}
    ARGS=${3}

    ssh_cmd "${NAME}"
    docker run --rm -t -w /target -v ${BUILD_DIR}:/target \
        ${IMAGE_PROMENADE} promenade validatedesign --href "${REF_URL}" "${ARGS}"
}

promenade_api_join_scripts() {
    NAME=${1}
    ARGS=${2}

    ssh_cmd "${NAME}"
    docker run --rm -t -w /target -v ${BUILD_DIR}:/target \
        ${IMAGE_PROMENADE} promenade join-scripts "${ARGS}" > "${SCRIPT_DIR}/join-${NAME}.sh"
    chmod 755 "${SCRIPT_DIR}/join-${NAME}.sh"
    rsync_cmd "${SCRIPT_DIR}/join-${NAME}.sh" "${NAME}:/root/promenade/"
}

promenade_teardown_node() {
    TARGET=${1}
    VIA=${2}

    ssh_cmd "${TARGET}" /usr/local/bin/promenade-teardown
    kubectl_cmd "${VIA}" delete node "${TARGET}"
}

promenade_render_curl_url() {
    NAME=${1}
    USE_DECKHAND=${2}
    DECKHAND_REVISION=${3}
    shift 3
    LABELS=(${@})

    LABEL_PARAMS=
    for label in "${LABELS[@]}"; do
        LABEL_PARAMS+="&labels.dynamic=${label}"
    done

    BASE_URL="${PROMENADE_BASE_URL}/api/v1.0/join-scripts"
    if [[ ${USE_DECKHAND} == 1 ]]; then
        DESIGN_REF="design_ref=deckhand%2Bhttp://deckhand-int.ucp.svc.cluster.local:9000/api/v1.0/revisions/${DECKHAND_REVISION}/rendered-documents"
    else
        DESIGN_REF="design_ref=${NGINX_URL}/promenade.yaml"
    fi
    HOST_PARAMS="hostname=${NAME}&ip=$(config_vm_ip "${NAME}")"

    echo "${BASE_URL}?${DESIGN_REF}&${HOST_PARAMS}&leave_kubectl=true${LABEL_PARAMS}"
}

promenade_render_validate_url() {
    echo "${PROMENADE_BASE_URL}/api/v1.0/validatedesign"
}

promenade_render_validate_body() {
    USE_DECKHAND=${1}
    DECKHAND_REVISION=${2}

    if [[ ${USE_DECKHAND} == 1 ]]; then
        JSON="{\"rel\":\"design\",\"href\":\"deckhand+http://deckhand-int.ucp.svc.cluster.local:9000/api/v1.0/revisions/${DECKHAND_REVISION}/rendered-documents\",\"type\":\"application/x-yaml\"}"
    else
        JSON="{\"rel\":\"design\",\"href\":\"${NGINX_URL}/promenade.yaml\",\"type\":\"application/x-yaml\"}"
    fi

    echo ${JSON}
}

promenade_health_check() {
    VIA=${1}
    log "Checking Promenade API health"
    MAX_HEALTH_ATTEMPTS=6
    for attempt in $(seq ${MAX_HEALTH_ATTEMPTS}); do
        if ssh_cmd "${VIA}" curl -v --fail "${PROMENADE_BASE_URL}/api/v1.0/health"; then
            log "Promenade API healthy"
            break
        elif [[ $attempt == "${MAX_HEALTH_ATTEMPTS}" ]]; then
            log "Promenade health check failed, max retries (${MAX_HEALTH_ATTEMPTS}) exceeded."
            exit 1
        fi
        sleep 10
    done
}
