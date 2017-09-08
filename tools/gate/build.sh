#!/usr/bin/env bash

set -ex

GATE_DIR=$(realpath $(dirname $0))
pushd $GATE_DIR

ENV_PATH=$GATE_DIR/config-env

if [ ! -s $ENV_PATH ]; then
    echo Environment variables for config substitution in $ENV_PATH are required.
    exit 1
fi

if [ "x$PROMENADE_IMAGE" = "x" ]; then
    echo PROMENADE_IMAGE environment variable must be supplied.
    exit 1
fi

echo === Building assets for testing ===
echo Usinag image ${PROMENADE_IMAGE}.

echo === Cleaning up old data ===
rm -f config/*
rm -f generated-scripts/*

echo === Validating test environment ===
env -i - $(cat default-config-env) env $(cat $ENV_PATH) $GATE_DIR/util/validate-test-env.sh

echo === Substituting variables into configuration ===
for template in config-templates/*; do
    OUTPUT_PATH=config/$(basename $template)
    env -i - $(cat default-config-env) env $(cat $ENV_PATH) envsubst < $template > $OUTPUT_PATH

    cat $OUTPUT_PATH
    echo
    echo
done

echo === Generating certificates ===
docker run --rm -t \
    -w /target \
    -v $GATE_DIR:/target \
    ${PROMENADE_IMAGE} \
        promenade \
            generate-certs \
                -o config \
                config/*.yaml

echo === Building genesis and join scripts
docker run --rm -t \
    -w /target \
    -v $GATE_DIR:/target \
    ${PROMENADE_IMAGE} \
        promenade \
            build-all \
                --validators \
                -o generated-scripts \
                config/*.yaml

echo === Bundling assets for delivery ===
tar czf promenade-bundle.tgz generated-scripts/*

echo === Done ===
