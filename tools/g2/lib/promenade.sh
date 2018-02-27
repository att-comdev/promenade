IMAGE_PROMENADE=${IMAGE_PROMENADE:-quay.io/attcomdev/promenade:latest}
SCRIPT_DIR=$(realpath $(dirname $0))
BUILD_DIR=$(realpath ${2:-${SCRIPT_DIR}/../build})

promenade_api_health() {
    NAME=${1}
    ARGS=${2}

    ssh_cmd "${NAME}"
    docker run --rm -t -w /target -v ${BUILD_DIR}:/target \
        ${IMAGE_PROMENADE} promenade check-health "${TOKEN}"
}

promenade_api_validatedesign() {
    NAME=${1}
    REF_URL=${2}
    ARGS=${3}

    ssh_cmd "${NAME}"
    docker run --rm -t -w /target -v ${BUILD_DIR}:/target \
        ${IMAGE_PROMENADE} promenade validatedesign --href "${REF_URL}" "${TOKEN}"
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
