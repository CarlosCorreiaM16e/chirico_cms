# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

from m16e.db import db_tables
from gluon import current
from gluon.storage import Storage
from m16e import term
from m16e.views.edit_base_view import BaseFormView

#------------------------------------------------------------------
class ConfigAppConfigView( BaseFormView ):
    def __init__( self, db ):
        super( ConfigAppConfigView, self ).__init__( db )
        self.table_model = db_tables.get_table_model( 'app_config', db=db )
        self.exclude_fields = [ 'flash_msg_delay' ]


    #------------------------------------------------------------------
    def process( self ):
        #------------------------------------------------------------------
        request = current.request
        response = current.response
        session = current.session
        cache = current.cache
        T = current.T
        db = self.db
        auth = session.auth
        redirect = None

        term.printLog( 'request.args: ' + repr( request.args ) )
        term.printLog( 'request.vars: ' + repr( request.vars ) )

        self.record_id = 1
        ac = self.table_model[ self.record_id ]
        if not ac:
            self.table_model.insert( dict() )
            ac = self.table_model[ self.record_id ]
        form = self.get_form()
        if form.accepts( request.vars, session ):
            response.flash = T( 'Configuration saved' )
        elif form.errors:
            term.printLog( 'errors: %s' % repr( form.errors ) )
            response.flash = T( 'Configuration error' )

        return Storage( dict=dict( form=form ,
                                   app_config=ac,
                                   panel_title=T( 'Application defaults' ) ),
                        redirect=redirect )


