# -*- coding: utf-8 -*-
# this file is released under GPL Licence v.3
# author: carlos@memoriapersistente.pt

import datetime

from m16e.db import db_tables
from gluon.globals import current
from gluon.html import DIV, P
from gluon.storage import Storage
from m16e import term


DT = datetime.datetime

#------------------------------------------------------------------
def update_task( shared_run_id,
                 sr_vars,
                 msg_title=None ):
    T = current.T
    db = current.db
    if not msg_title:
        msg_title = T( 'Task running' )
    sr_vars = Storage( sr_vars )
    sr_model = db_tables.get_table_model( 'shared_run' )
    sr = sr_model[ shared_run_id ]
    if not sr.running_since:
        sr_vars.running_since = DT.now()
    sr_model.update_by_id( shared_run_id, sr_vars )
    if sr_vars.notify_user:
        um_model = db_tables.get_table_model( 'user_message', db=db )
        msg_div = DIV( _class='msg_success' )
        msg_div.append( P( sr_vars.progress_message ) )
        um_model.update_by_id( sr.progress_msg_id,
                               dict( msg_text=msg_div.xml(),
                                     ack_when=None ) )

#------------------------------------------------------------------
def schedule_task( long_task_id,
                   task_parameters='',
                   requested_when=DT.now(),
                   requested_by=None,
                   msg_title=None,
                   msg_text=None,
                   display_from=DT.now() ):
    db = current.db
    sr_model = db_tables.get_table_model( 'shared_run', db=db )
    sr_vars = Storage( requested_when=requested_when,
                       notify_user=bool( requested_by ) )
    sr = None
    if requested_by:
        q_sql = (db.shared_run.requested_by == requested_by)
        q_sql &= (db.shared_run.long_task_id == long_task_id)
        q_sql &= (db.shared_run.task_parameters == task_parameters)
        q_sql &= (db.shared_run.finished_when == None)
        sr = sr_model.select( q_sql ).first()
        um_model = db_tables.get_table_model( 'user_message' )
        um_id = um_model.insert( dict( notify_user_id=requested_by,
                                       msg_title=msg_title,
                                       msg_text=msg_text,
                                       period_start=display_from ) )
        sr_vars.progress_msg_id = um_id
    if not sr:
        sr_vars.long_task_id = long_task_id
        sr_vars.task_parameters = task_parameters
        sr_vars.requested_by = requested_by
        sr = sr_model.insert( sr_vars )
    else:
        sr_model.update_by_id( sr.id, sr_vars )
    term.printDebug( 'task created: %s as:\n%s' %
                     (str( sr.id ), repr( sr_vars )) )
    return sr
