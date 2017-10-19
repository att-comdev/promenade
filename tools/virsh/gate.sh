#!/usr/bin/env bash

set -e

SCRIPT_DIR=$(realpath $(dirname $0))

C_CLEAR="\e[0m"
C_ERROR="\e[38;5;160m"
C_HEADER="\e[38;5;164m"
C_HILIGHT="\e[38;5;27m"
C_SUCCESS="\e[38;5;46m"


SETUP_SCRIPT=$(realpath $(jq -cr '.setup.script' $SCRIPT_DIR/gate/manifest.json))

echo -e "${C_HEADER}=== Executing ${C_HILIGHT}Setup${C_HEADER} ===${C_CLEAR}"
if bash $SETUP_SCRIPT ; then
    echo -e " ${C_SUCCESS}== Setup Success ==${C_CLEAR}"
else
    echo -e " ${C_ERROR}== Setup Error ==${C_CLEAR}"
    exit 1
fi
echo -e "${C_HEADER}=== Finished ${C_HILIGHT}Setup${C_HEADER} ===${C_CLEAR}"

STAGES=$(mktemp)
jq -cr '.stages | .[]' $SCRIPT_DIR/gate/manifest.json > $STAGES

# NOTE(mark-burnett): It is necessary to use a non-stdin file descriptor for
# the read below, since we will be calling SSH, which will consume the
# remaining data on STDIN.
exec 3< $STAGES
while read -u 3 stage; do
    NAME=$(echo ${stage} | jq -r .name)
    SCRIPT=$(realpath $(echo ${stage} | jq -r .script))

    if echo ${stage} | jq -e .arguments > /dev/null; then
        ARGUMENTS=($(echo ${stage} | jq -r '.arguments[]'))
    else
        ARGUMENTS=()
    fi

    echo -e "${C_HEADER}=== Executing stage ${C_HILIGHT}${NAME}${C_HEADER} ===${C_CLEAR}"
    if bash $SCRIPT ${ARGUMENTS[*]}; then
        echo -e "${C_CLEAR}"
        echo -e " ${C_SUCCESS}== Stage Success ==${C_CLEAR}"
    else
        echo -e "${C_CLEAR}"
        echo -e " ${C_ERROR}== Stage Error ==${C_CLEAR}"
        if echo ${stage} | jq -e .on_error > /dev/null; then
            echo -e "  ${C_ERROR}= Diagnostic Report =${C_CLEAR}"
            ON_ERROR=$(realpath $(echo ${stage} | jq -r .on_error))
            set +e
            bash $ON_ERROR
        fi
        exit 1
    fi
    echo -e "${C_HEADER}=== Finished stage ${C_HILIGHT}${NAME}${C_HEADER} ===${C_CLEAR}"
done


echo
echo -e "${C_SUCCESS}=== HUGE SUCCESS ===${C_CLEAR}"
