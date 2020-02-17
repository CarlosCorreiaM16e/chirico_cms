#!/bin/bash -x

find -L . -name "*.pyc" |xargs rm -f
set -e
dropdb --if-exists chirico__cms
set +e
createdb chirico__cms

python web2py.py -i 127.0.0.1 -p 8001 -M -S www \
    -R applications/www/resources/scripts/init_app.py


