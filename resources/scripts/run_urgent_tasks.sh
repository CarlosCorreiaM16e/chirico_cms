#!/bin/sh
# run as www-data, via crontab
# install at /www/resources/scripts

set -e

LOG_DIR=/home/www-data/.log/chirico__cms/cronjobs/tasks
mkdir -p $LOG_DIR
TIME_NOW=`date +%Y-%m-%d-%H-%M`
LOG_FILE=$LOG_DIR/run-long-tasks-$TIME_NOW.log

date > $LOG_FILE 2>&1

python /home/www-data/sites/mia/web2py/current/web2py.py \
	--port=8001 -S www/cronjobs/run_urgent_tasks >> $LOG_FILE 2>&1

echo "Finished: " $? >> $LOG_FILE 2>&1
date >> $LOG_FILE 2>&1
