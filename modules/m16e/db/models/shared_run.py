# -*- coding: utf-8 -*-

import datetime

from app.db_sets import SR_OK, SR_ERROR
from gluon import current
from gluon.dal import Field
from gluon.validators import IS_IN_SET
from m16e.db.database import DbBaseTable

DT=datetime.datetime
DATE=datetime.date

#----------------------------------------------------------------------
class SharedRunModel( DbBaseTable ):
    table_name = 'shared_run'

    #----------------------------------------------------------------------
    def __init__( self, db ):
        super( SharedRunModel, self ).__init__( db )

    #----------------------------------------------------------------------
    def get_fields( self ):
        self.fields = [ Field( 'long_task_id', 'integer', notnull=True ),
                        Field( 'task_parameters', 'string' ),
                        Field( 'progress_message', 'string' ),
                        Field( 'requested_by', 'integer' ),
                        Field( 'requested_when', 'datetime', default=DT.now() ),
                        Field( 'start_at', 'datetime', default=DT.now(), notnull=True ),
                        Field( 'running_since', 'datetime' ),
                        Field( 'finished_when', 'datetime' ),
                        Field( 'finished_status', 'string' ),
                        Field( 'percent_done', 'integer', default=0, notnull=True ),
                        Field( 'notify_user', 'boolean', default=True, notnull=True ),
                        Field( 'user_notified_when', 'datetime' ),
                        Field( 'progress_msg_id', 'integer' ),
                        Field( 'priority', 'integer', default=100, notnull=True ),
                        ]
        return self.fields

    #----------------------------------------------------------------------
    def get_validators( self ):
        T = current.T
        self.validators = { 'finished_status': IS_IN_SET( [ (SR_OK, T( 'OK' )),
                                                            (SR_ERROR, T( 'Error' )) ] ),
                           }
        return self.validators
    #----------------------------------------------------------------------

