#!/usr/bin/env bash

set -e

SCRIPT_DIR=$(realpath $(dirname $0))
export WORKSPACE=$(realpath ${SCRIPT_DIR}/..)
export GATE_UTILS=${WORKSPACE}/tools/g2/lib/all.sh
export TEMP_DIR=$(mktemp -d)
chmod -R 755 ${TEMP_DIR}

MANIFEST_ARG=${1:-full}
MANIFEST=${WORKSPACE}/tools/g2/manifests/${MANIFEST_ARG}.json

# XXX This will move to gate utils
C_CLEAR="\e[0m"
C_ERROR="\e[38;5;160m"
C_HEADER="\e[38;5;164m"
C_HILIGHT="\e[38;5;27m"
C_TEMP="\e[38;5;226m"
C_SUCCESS="\e[38;5;46m"

STAGES_DIR=${WORKSPACE}/tools/g2/stages

echo -e Working in ${C_TEMP}${TEMP_DIR}${C_CLEAR}
echo

STAGES=$(mktemp)
jq -cr '.stages | .[]' ${MANIFEST} > ${STAGES}

# NOTE(mark-burnett): It is necessary to use a non-stdin file descriptor for
# the read below, since we will be calling SSH, which will consume the
# remaining data on STDIN.
exec 3< $STAGES
while read -u 3 stage; do
    NAME=$(echo ${stage} | jq -r .name)
    STAGE_CMD=${STAGES_DIR}/$(echo ${stage} | jq -r .script)

    if echo ${stage} | jq -e .arguments > /dev/null; then
        ARGUMENTS=($(echo ${stage} | jq -r '.arguments[]'))
    else
        ARGUMENTS=()
    fi

    echo -e "${C_HEADER}=== Executing stage ${C_HILIGHT}${NAME}${C_HEADER} ===${C_CLEAR}"
    if $STAGE_CMD ${ARGUMENTS[*]}; then
        echo -e " ${C_SUCCESS}== Stage Success ==${C_CLEAR}"
    else
        echo -e "${C_CLEAR}"
        echo -e " ${C_ERROR}== Error in stage ${C_HILIGHT}${NAME}${C_ERROR} ( ${C_TEMP}${TEMP_DIR}${C_ERROR} ) ==${C_CLEAR}"
        if echo ${stage} | jq -e .on_error > /dev/null; then
            echo -e "  ${C_ERROR}= Diagnostic Report =${C_CLEAR}"
            ON_ERROR=${WORKSPACE}/$(echo ${stage} | jq -r .on_error)
            set +e
            $ON_ERROR
        fi
        exit 1
    fi
    echo -e "${C_HEADER}=== Finished stage ${C_HILIGHT}${NAME}${C_HEADER} ===${C_CLEAR}"
    echo
done


echo
echo -e "${C_SUCCESS}=== HUGE SUCCESS ===${C_CLEAR}"
