# -*- coding: utf-8 -*-

import datetime

from app import db_sets
from gluon.dal import Field
from gluon.validators import IS_IN_DB, IS_IN_SET
from m16e.db.database import DbBaseTable

DT = datetime.datetime
DATE = datetime.date

# THUMBS_EXT = [
#     'bmp',
#     'gif',
#     'jpeg',
#     'jpg',
#     'pcx',
#     'pbm',
#     'pgm',
#     'png',
#     'ppm',
#     'tiff',
#     'tif',
#     'xbm',
#     'xmp'
# ]

#------------------------------------------------------------------
class MailQueueModel( DbBaseTable ):
    table_name = 'mail_queue'

    #------------------------------------------------------------------
    def __init__( self, db ):
        super( MailQueueModel, self ).__init__( db )

    #------------------------------------------------------------------
    def get_fields( self ):
        self.fields = [ Field( 'subject', 'string', notnull='True' ),
                        Field( 'text_body', 'text' ),
                        Field( 'html_body', 'text' ),
                        Field( 'when_to_send', 'datetime', default=DT.now(), notnull='True' ),
                        Field( 'sent', 'datetime' ),
                        Field( 'status', 'string', default='', notnull='True' ),
                        Field( 'mail_cc', 'string' ),
                        Field( 'mail_bcc', 'string' ),
                        # Field( 'task_id', 'reference scheduler_task' ),
                        Field( 'auth_user_id', 'reference auth_user', notnull='True' ),
                        Field( 'percent_done', 'integer', default=0, notnull='True' ),
                        Field( 'progress_message', 'string' ),
                        ]
        return self.fields

    #------------------------------------------------------------------
    def get_validators( self ):
        self.validators = { 'auth_user_id': IS_IN_DB( self.db, 'auth_user.id', '%(first_name)s (%(email)s)', zero=None ),
                            # 'task_id': IS_IN_DB( self.db, 'scheduler_task.id', 'scheduler_task.name', zero=None ),
                            'status': IS_IN_SET( db_sets.MQ_STATUS_SET )
                            }
        return self.validators

