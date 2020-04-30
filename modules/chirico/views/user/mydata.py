# -*- coding: utf-8 -*-

from gluon import current, SPAN, SQLFORM, URL, SCRIPT, DIV, IS_IN_SET, IS_NOT_IN_DB, Field
from gluon.storage import Storage
from m16e import term, htmlcommon
from m16e.db import db_tables
from m16e.db.database import DbBaseTable
from m16e.views.edit_base_view import BaseFormView

MAX_ZIP_HELPER_ROWS = 50


class CmsUserMydataView( BaseFormView ):
    controller_name = 'user'
    function_name = 'mydata'

    def __init__( self, db ):
        super( CmsUserMydataView, self ).__init__( db )
        self.table_model = db_tables.get_table_model( 'user_data', db=db )


    def do_process( self ):
        return super( CmsUserMydataView, self ).do_process()


    def fetch_record_id( self ):
        auth = current.auth
        db = self.db
        q_sql = (db.user_data.auth_user_id == auth.user.id)
        self.record = self.table_model.select( q_sql ).first()
        if not self.record:
            auth = current.auth
            self.record_id = self.table_model.insert( dict( auth_user_id=auth.user.id ) )
            self.record = self.table_model[ self.record_id ]
        self.record_id = self.record.id


    def get_form_fields( self ):
        self.form_fields = [ Field( 'id', 'integer' ) ]
        v_dict = self.table_model.get_validators()
        for f in self.table_model.fields:
            if f.name == 'auth_user_id':
                continue
            if f.name in v_dict:
                f.requires = v_dict[ f.name ]
            self.form_fields.append( f )

        self.form_fields.append( Field( 'first_name', 'string', notnull=True ) )
        self.form_fields.append( Field( 'email', 'string', notnull=True ) )
        return self.form_fields


    def get_form( self,
                  form_fields=None,
                  form_validators=None,
                  deletable=None,
                  textarea_rows=None,
                  readonly_fields=None,
                  exclude_fields=None,
                  upload=None,
                  showid=None,
                  buttons=None,
                  extra_fields=None,
                  form_id=None ):
        term.printDebug( 'form_validators: %s' % repr( form_validators ) )
        form = SQLFORM.factory( *self.get_form_fields() )
        for f in self.table_model.fields:
            if f.name in( 'auth_user_id', 'user_data_id'):
                continue
            form.vars[ f.name ] = self.record[ f.name ]
        auth = current.auth
        form.vars.first_name = auth.user.first_name
        form.vars.email = auth.user.email

        return form


    def update_record( self, upd ):
        super( CmsUserMydataView, self ).update_record( upd )
        db = self.db
        au_upd = Storage()
        if 'first_name' in upd:
            au_upd.first_name = upd.first_name
        if 'email' in upd:
            au_upd.email = upd.email
        if au_upd:
            db( db.auth_user.id == self.record.auth_user_id).update( **au_upd )


    def process_form( self, form ):
        super( CmsUserMydataView, self ).process_form( form )


    def post_process_form( self, form ):
        super( CmsUserMydataView, self ).post_process_form( form )
        db = self.db
        auth = current.auth
        self.set_result( data=dict( form=form, auth_user=auth.user ) )


