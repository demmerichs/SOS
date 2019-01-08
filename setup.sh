#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

if [ -d "$DIR/venv" ]
then
    :
else
    virtualenv $DIR/venv -p python3
fi

source $DIR/venv/bin/activate
pip3 install -U pip
pip3 install -U -r $DIR/requirements.txt
