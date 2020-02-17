# -*- coding: utf-8 -*-

from gluon import IS_IN_SET, IS_IN_DB
from gluon.dal import Field
from m16e.db.database import DbBaseTable
from m16e.kommon import MSG_TYPE_RESPONSE, MSG_TYPE_SET, DT


class UserMessageModel( DbBaseTable ):
    table_name = 'user_message'


    def __init__( self, db ):
        super( UserMessageModel, self ).__init__( db )


    def get_fields( self ):
        self.fields = [ Field( 'notify_user_id', 'reference auth_user', notnull=True ),
                        Field( 'msg_org', 'integer' ),
                        Field( 'msg_type', 'integer', default=MSG_TYPE_RESPONSE[0], notnull=True,
                               requires=IS_IN_SET( MSG_TYPE_SET ) ),
                        Field( 'msg_title', 'string', notnull=True ),
                        Field( 'msg_text', 'string', notnull=True ),
                        Field( 'times_viewed', 'integer', default=0, notnull=True ),
                        Field( 'period_start', 'datetime', default=DT.now(), notnull=True ),
                        Field( 'period_stop', 'datetime' ),
                        Field( 'ack_when', 'datetime' ),
                        Field( 'answer', 'string' ),
                        Field( 'delete_if_past', 'boolean', default=False, notnull=True ),
        ]
        return self.fields


    def get_validators( self ):
        self.validators = { 'notify_user_id': IS_IN_DB( self.db, 'auth_user.id', '%(first_name)s (%(email)s)' )}
        return self.validators


