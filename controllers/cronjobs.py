# -*- coding: utf-8 -*-

import datetime
import os
import sys
import traceback
from decimal import Decimal

from m16e.db import db_tables
from m16e import term, mpmail

if 0:
    import gluon
    import gluon.languages.translator as T

    global auth; auth = gluon.tools.Auth()
    global mail; mail = mail=auth.settings.mailer
    global cache; cache = gluon.cache.Cache()
    global crud; crud = gluon.tools.Crud()
    global db; db = gluon.DAL()
    global request; request = gluon.globals.Request()
    global response; response = gluon.globals.Response()
    global service; service = gluon.tools.Service()
    global session; session = gluon.globals.Session()

MAX_RETRIES = 5

def sendmails():
    mq_model = db_tables.get_table_model( 'mail_queue', db=db )
    mr_model = db_tables.get_table_model( 'mail_recipient', db=db )
    q_sql = (db.mail_queue.status != 'sent')
    mq_list = mq_model.select( q_sql, orderby='when_to_send' )
    try:
        for mq in mq_list:
            success = 0
            fail = 0
            sent_ts = datetime.datetime.now()
            q_sql = (db.mail_recipient.mail_queue_id == mq.id)
            q_sql &= (db.mail_recipient.status != 'sent')
            q_sql &= (db.mail_recipient.retries < MAX_RETRIES)
            mr_list = mr_model.select( q_sql )
            for mr in mr_list:
                to = mr.email
                try:
                    mpmail.do_send_mail( to,
                                         cc=mq.mail_cc,
                                         bcc=mq.mail_bcc,
                                         subject=mq.subject,
                                         message=mq.text_body )

                    mr_model.update_by_id( mr.id,
                                           dict( sent=sent_ts,
                                                 status='sent' ) )
                    db.commit()
                    success += 1
                except:
                    fail += 1
                    db.rollback()
                    t, v, tb = sys.exc_info()
                    traceback.print_exception( t, v, tb )
                    sql = '''
                        update mail_recipient 
                        set retries = retries + 1, status='error' 
                        where id = %d''' % mr.id
                    db.executesql( sql )
                    db.commit()

            if fail:
                q_sql = (db.mail_recipient.mail_queue_id == mq.id)
                mr_count = float( mr_model.count( q_sql ) )
                q_sql &= (db.mail_recipient.status == 'sent')
                mr_done = float( mr_model.count( q_sql ) )
                mq_model.update_by_id( mq.id,
                                       dict( sent=sent_ts,
                                             status='error',
                                             percent_done=int( mr_done / mr_count * 100 ) ) )
            else:
                mq_model.update_by_id( mq.id,
                                       dict( sent=sent_ts,
                                             status='sent',
                                             percent_done=100 ) )

                db.commit()
                term.printDebug( 'mail sent' )
    except:
        db.rollback()
        t, v, tb = sys.exc_info()
        traceback.print_exception( t, v, tb )


def run_long_tasks( dummy=False ):
    lt_model = db_tables.get_table_model( 'long_task' )
    sr_model = db_tables.get_table_model( 'shared_run' )
    q_sql = (db.shared_run.running_since == None)
    q_sql &= (db.shared_run.finished_status == None)
    sr_list = sr_model.select( q_sql, orderby='priority' )
    term.printDebug( 'rows: %s' % len( sr_list ) )
    for sr in sr_list:
        term.printDebug( 'sr: %s' % repr( sr ) )
        lt = lt_model[ sr.long_task_id ]
        if lt.force_single_instance:
            q_sql = (db.shared_run.long_task_id == lt.id)
            q_sql &= (db.shared_run.percent_done > 0)
            q_sql &= (db.shared_run.percent_done < 100)
            running_lt_list = sr_model.select( q_sql )
            if running_lt_list:
                term.printLog( 'Still running task: %s' % repr( running_lt_list[0] ) )
                continue
    db.commit()


def run_urgent_tasks( dummy=True ):
    try:
        run_long_tasks()
        sendmails()
    except:
        t, v, tb = sys.exc_info()
        traceback.print_exception( t, v, tb )


