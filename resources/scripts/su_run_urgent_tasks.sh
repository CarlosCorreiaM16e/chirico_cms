#!/bin/sh
# run as root, via crontab
# install at /www/resources/scripts

set -e

RUN=$(psql -U carlos -h localhost -At  -c "select * from shared_run where running_since is null and finished_status is null and start_at <= now() order by priority, id desc" mia__www)
if [ -z "$RUN" ]
then
    RUN=$(psql -U carlos -h localhost -At  -c "select * from mail_queue where status != 'sent' and when_to_send <= now() order by when_to_send, id" mia__www)
fi

# echo $RUN
W2P_FOLDER='/home/www-data/sites/mia/web2py/current'
SCRIPTS_FOLDER=$W2P_FOLDER'/applications/www/resources/scripts'

sudo -u www-data mkdir -p $W2P_FOLDER/applications/www/var/run
RUNNING_FLAG=$W2P_FOLDER'/applications/www/var/run/RUNNING_URGENT_TASKS'

sudo -u www-data mkdir -p /home/www-data/.log/mia__www/cronjobs/tasks

# if no tasks to run
if [ -z "$RUN" ]
then
    sudo -u www-data touch /home/www-data/.log/mia__www/cronjobs/tasks/last_empty_run
elif [ -f $RUNNING_FLAG ]
then
    sudo -u www-data touch /home/www-data/.log/mia__www/cronjobs/tasks/last_skipped_run
else
#    /etc/init.d/postgresql restart
    sudo -u www-data touch $RUNNING_FLAG
    sudo -u www-data $SCRIPTS_FOLDER/run_urgent_tasks.sh
    sudo -u www-data rm $RUNNING_FLAG
    # log in: /home/www-data/.log/mia__www/cronjobs/tasks/run-long-tasks-$TIME_NOW.log
fi


