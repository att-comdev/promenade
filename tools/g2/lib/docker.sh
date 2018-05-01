docker_build_promenade() {
    CONFIG_PROXY=${HTTP_PROXY:-}

    log Building docker image "${IMAGE_PROMENADE}"

    if [[ -z "$CONFIG_PROXY" ]]
    then
      docker build -q \
        --network host \
        -t "${IMAGE_PROMENADE}" \
        "${WORKSPACE}"
    else
        docker build -q \
          --network host \
          -t "${IMAGE_PROMENADE}" \
          --build-arg "HTTP_PROXY=${HTTP_PROXY:-}" \
          --build-arg "HTTPS_PROXY=${HTTPS_PROXY:-}" \
          --build-arg "NO_PROXY=${NO_PROXY:-}" \
          --build-arg "http_proxy=${http_proxy:-}" \
          --build-arg "https_proxy=${https_proxy:-}" \
          --build-arg "no_proxy=${no_proxy:-}" \
          "${WORKSPACE}"
    fi

    log Loading Promenade image "${IMAGE_PROMENADE}" into local registry
    docker tag "${IMAGE_PROMENADE}" "localhost:5000/${IMAGE_PROMENADE}" &>> "${LOG_FILE}"
    docker push "localhost:5000/${IMAGE_PROMENADE}" &>> "${LOG_FILE}"
}

docker_ps() {
    VIA="${1}"
    ssh_cmd "${VIA}" docker ps -a
}

docker_info() {
    VIA="${1}"
    ssh_cmd "${VIA}" docker info 2>&1
}

docker_exited_containers() {
    VIA="${1}"
    ssh_cmd "${VIA}" docker ps -q --filter "status=exited"
}

docker_inspect() {
    VIA="${1}"
    CONTAINER_ID="${2}"
    ssh_cmd "${VIA}" docker inspect "${CONTAINER_ID}"
}

docker_logs() {
    VIA="${1}"
    CONTAINER_ID="${2}"
    ssh_cmd "${VIA}" docker logs "${CONTAINER_ID}"
}
