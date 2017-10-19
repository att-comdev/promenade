#!/usr/bin/env bash

set -e

source ${GATE_UTILS}

vm_clean ${GENESIS_NAME}
vm_create ${GENESIS_NAME}

rsync_cmd ${TEMP_DIR}/scripts/*${GENESIS_NAME}* ${GENESIS_NAME}:/root/promenade/

ssh_cmd ${GENESIS_NAME} /root/promenade/join-${GENESIS_NAME}.sh
ssh_cmd ${GENESIS_NAME} /root/promenade/validate-${GENESIS_NAME}.sh
