#!/bin/bash -x

APP_NAME='www'

find . -name '*.pyc' | xargs rm
python web2py.py -i localhost -M -S $APP_NAME \
    -R applications/$APP_NAME/resources/upgrades/deploy/farmer.py -A $* applications/$APP_NAME/private/cfg_$APP_NAME.py

