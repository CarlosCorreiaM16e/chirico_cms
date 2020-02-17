# -*- coding: utf-8 -*-

import datetime

from gluon.dal import Field
from gluon.validators import IS_IN_DB
from m16e.db.database import DbBaseTable

DT = datetime.datetime
DATE = datetime.date

#------------------------------------------------------------------
class MailRecipientModel( DbBaseTable ):
    table_name = 'mail_recipient'

    #------------------------------------------------------------------
    def __init__( self, db ):
        super( MailRecipientModel, self ).__init__( db )

    #------------------------------------------------------------------
    def get_fields( self ):
        from m16e.db import db_tables
        db_tables.get_table_model( 'mail_queue', db=self.db )
        self.fields = [ Field( 'mail_queue_id', 'reference mail_queue', ondelete='NO ACTION', notnull = 'True' ),
                        Field( 'email', 'string', notnull = 'True' ),
                        Field( 'sent', 'datetime' ),
                        Field( 'status', 'string', notnull=True, default='pending' ),
                        Field( 'retries', 'integer' ),
                        ]
        return self.fields

    #------------------------------------------------------------------
    def get_validators( self ):
        from m16e.db import db_tables
        db_tables.get_table_model( 'mail_queue', db=self.db )
        self.validators = { 'mail_queue_id': IS_IN_DB( self.db,
                                                       'mail_queue.id',
                                                       'mail_queue.subject',
                                                       zero=None ),
                           }
        return self.validators

