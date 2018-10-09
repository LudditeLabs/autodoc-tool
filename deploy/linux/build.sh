#!/usr/bin/env bash

export TERM=xterm-256color
red='\E[31m'
green='\E[32m'
yellow='\E[33m'
clear='\E[0m'


function msg_error() {
    echo -e $red"$@"$clear
}

function check_run() {
    "$@"
    local status=$?
    if [[ $status != 0 ]]; then
        msg_error "Error running [$1]"
        exit $status
    fi
}

function asuser() {
    check_run su-exec "${ASUID:-1000}:${ASUID:-1000}" "$@"
}

cd src/contentdb && asuser mkdir -p build && cd build
asuser cmake -G"Unix Makefiles" \
    -DPYTHON_INCLUDE_DIR=${PYENV_ROOT}/versions/3.6.6/include/python3.6m \
    -DPYTHON_LIBRARY=${PYENV_ROOT}/versions/3.6.6/lib/libpython3.6m.so \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=/project/src/contentdb/install \
    ..
asuser make install -j 4

cd /project
check_run pip install . && python -m pip uninstall -y autodoc  # Install deps
cd deploy
asuser python cxsetup.py bdist_zip
