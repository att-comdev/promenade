validate_cluster() {
    NAME=${1}

    log Validating cluster via VM ${NAME}
    rsync_cmd ${TEMP_DIR}/scripts/validate-cluster.sh ${NAME}:/root/promenade/
    ssh_cmd ${NAME} /root/promenade/validate-cluster.sh
}
