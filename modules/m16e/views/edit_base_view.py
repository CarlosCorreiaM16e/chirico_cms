# -*- coding: utf-8 -*-

import sys
import traceback
from psycopg2 import Error, errorcodes

from gluon.globals import current
from gluon.html import URL
from gluon.sqlhtml import SQLFORM
from gluon.storage import Storage
from m16e import term, htmlcommon
from m16e.db.database import DatabaseException, DbBaseTable
from m16e.decorators import deprecated
from m16e.kommon import KQK_PREFIX, KQV_PREFIX, ACT_DELETE_RECORD, \
    ACT_SUBMIT, K_ROLE_DEVELOPER, K_ROLE_ADMIN, K_ROLE_MANAGER, K_ROLE_EDITOR, K_ROLE_SUPPORT
from m16e.ktfact import KTF_ACTION
from m16e.ui.actions import UiAction
from m16e.ui.elements import UiButton, UiIcon, BTN_SUBMIT, ICON_SAVE
from m16e.user_factory import is_in_group
from m16e.views.base_view import BaseView
from m16e.views.plastic_view import BT_SUBMIT_ID

CKB_DELETE_RECORD_NAME = 'delete_this_record'
CKB_DELETE_RECORD_ID = 'delete_this_record'


class BaseFormView( BaseView ):
    function_name = 'edit'

    #------------------------------------------------------------------
    def __init__( self, db ):
        super( BaseFormView, self ).__init__( db )

        T = current.T
        self.delete_action = ACT_DELETE_RECORD

        self.msg_record_updated = T( 'Record updated' )
        self.msg_record_created = T( 'Record created' )
        self.msg_record_deleted = T( 'Record deleted' )
        self.msg_nothing_to_update = T( 'Nothing to update' )

        self.msg_form_title = ''

        self.record_id = None
        self.record = None

        self.form_fields = None
        self.form_validators = {}
        self.deletable = False
        self.textarea_rows = 3
        self.readonly_fields = []
        self.exclude_fields = []
        self.upload = None
        self.showid = True
        self.buttons = [ UiButton( text=T( 'Submit' ),
                                   ui_icon=UiIcon( ICON_SAVE ),
                                   tip=T( 'Submit changes' ),
                                   action=UiAction( action_name=ACT_SUBMIT ),
                                   input_id=BT_SUBMIT_ID,
                                   button_style=BTN_SUBMIT ).get_html_button() ]
        self.fk_error = None
        self.fld_prefix = ''
        self.changed_fields = []


    def get_form_fields( self ):
        return self.form_fields


    #------------------------------------------------------------------
    def get_form_fields_placeholders( self ):
        return Storage()


    #------------------------------------------------------------------
    def get_form_extra_fields( self ):
        return None


    #------------------------------------------------------------------
    def get_default_values( self ):
        return Storage()


    #------------------------------------------------------------------
    def get_form_validators( self ):
#         term.printDebug( 'ping' )
#         term.printDebug( 'form_validators: %s' % repr( self.form_validators ) )
        return self.form_validators

    #------------------------------------------------------------------
    def get_readonly_fields( self ):
        return self.readonly_fields

    #------------------------------------------------------------------
    def get_exclude_fields( self ):
        return self.exclude_fields


    def get_pre_populated_vars( self ):
        return dict()


    def get_changed_fields( self,
                            form,
                            field_prefix='',
                            get_all=False,
                            db_table=None ):
        request = current.request
        if not db_table:
            db_table = self.get_db_table()
        upd = Storage()
        try:
            currency_list = current.currency_list
        except AttributeError as e:
            currency_list = None
        # term.printDebug( 'field_prefix: %s' % repr( field_prefix ),
        #                  print_trace=True )
        # term.printLog( 'form.vars: ' + repr( form.vars ) )
        # term.printLog( 'request.post_vars: ' + repr( request.post_vars ) )
        # term.printLog( 'field_prefix: ' + repr( field_prefix ) )
        for fld in db_table.fields:
            db_field_name = field_prefix + fld
            in_form_vars = db_field_name in form.vars
            in_req_vars = db_field_name in request.post_vars
            in_exclude = fld in self.exclude_fields
            in_ro = fld in self.readonly_fields
            if not in_form_vars and not in_req_vars or in_exclude or in_ro:
            #
            # if not db_field_name in form.vars \
            # and not db_field_name in request.post_vars \
            # or fld in self.exclude_fields \
            # or fld in self.readonly_fields:
                term.printDebug( 'Field \'%s\' not in form' % db_field_name )
                continue

            db_value = request.post_vars[ 'org__' + db_field_name ]
            (found, c_value) = self.get_constant_value( fld )
            if found:
                form_value = c_value
            else:
                form_value = request.post_vars[ db_field_name ]
                if form_value is None:
                    form_value = form.vars.get( db_field_name )
                # form_value = form.vars.get( db_field_name )
                # if form_value is None:
                #     form_value = request.post_vars[ db_field_name ]
            # term.printDebug(
            #     '>>> (UPD) vDb[%s]: %s: %s\n  vForm (%s): %s\n  req (%s): %s' %
            #     (db_field_name, repr( db_value ),
            #      db_table[ fld ].type,
            #      type( form_value ),
            #      repr( form_value ),
            #      type( request.vars[ db_field_name ] ),
            #      repr( request.vars[ db_field_name ] ) ), )

            if db_value is None and form_value == '':
                form_value = None

            if form_value is None and db_table[ fld ].notnull:
                form_value = db_table[ fld ].default

            if db_table[ fld ].type == 'boolean':
                if form_value == 'on' or form_value == True:
                    form_value = True
                else:
                    form_value = False
#                 term.printDebug( 'form_value( %s): %s' % ( fld, repr( form_value ) ) )
            elif db_table[ fld ].type == 'double':
                # term.printDebug( 'form_value( %s): %s (type: %s)' % ( fld, repr( form_value ), type( form_value ) ) )
                if isinstance( form_value, basestring ):
                    if currency_list:
                        for c in currency_list:
                            form_value = form_value.replace( c.currency_symbol, '' ).strip( )
                    form_value = form_value.replace( '%', '' ).strip()
                    form_value = form_value.replace( current.currency.symbol, '' ).strip()

            if db_table[ fld ].notnull \
            and ( db_table[ fld ].type == 'integer'
                  or db_table[ fld ].type.startswith( 'reference ' ) ):
                if form_value is not None:
                    form_value = int( form_value )
                else:
                    form_value = None

#                 term.printDebug(
#                     '>>> (UPD) vDb[%s]: %s; vForm: %s' %
#                     (db_field_name, repr( db_value ), repr( form_value )) )
            if get_all or str( db_value ) != str( form_value ):
    #             term.printDebug(
    #                 '>>> (UPD) vDb[%s]: %s; vForm: %s' %
    #                 (db_field_name, db_value, form_value) )
                upd[fld] = form_value
                if str( db_value ) != str( form_value ):
                    self.changed_fields.append( fld )
            # else:
            # if fld == 'is_controlling_existence':
            #     term.printDebug(
            #         '>>> (UPD) vDb[%s]: %s; vForm: %s' %
            #         (db_field_name, db_value, form_value) )

#         term.printDebug( 'upd: ' + repr( upd ) )
        return upd


    def process_pre_validation_actions( self ):
        term.printDebug( 'self.action: %s' % self.action )
        request = current.request
        if self.action == self.delete_action:
            delete = request.vars.get( CKB_DELETE_RECORD_NAME )
            if delete:
                self.try_to_delete_record()


    def append_org_fields( self,
                           form,
                           prefix=None ):
        if prefix is None:
            prefix = self.fld_prefix
        if self.record:
            for f in self.record:
                fld_name = 'org__' + prefix + f
                form.append( htmlcommon.get_input_field( fld_name,
                                                         input_id=fld_name,
                                                         value=self.record[ f ],
                                                         css_class='hidden' ) )
        return form



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
#         term.printDebug( 'db_record: %s' % repr( db_record ) )
#         term.printDebug( 'self.table_model.db: %s' % repr( self.table_model.db ) )
#         term.printDebug( 'self.table_model.table_name: %s' % repr( self.table_model.table_name ) )

        db = self.db
#         term.printDebug( 'form_validators: %s' % repr( form_validators ) )

        if form_fields is None:         form_fields = self.get_form_fields()
        if form_validators is None:     form_validators = self.get_form_validators()
#         term.printDebug( 'form_validators: %s' % repr( form_validators ) )

        if deletable is None:           deletable = self.deletable
        if textarea_rows is None:       textarea_rows = self.textarea_rows
        if readonly_fields is None:     readonly_fields = self.get_readonly_fields()
        if exclude_fields is None:      exclude_fields = self.get_exclude_fields()
        if upload is None:              upload = self.upload
        if showid is None:              showid = self.showid
        if buttons is None:             buttons = self.buttons
        if extra_fields is None:        extra_fields = self.get_form_extra_fields()

        # term.printDebug( 'exclude_fields: %s' % repr( exclude_fields ) )
        # if self.table_model and isinstance( self.table_model, DbBaseTable ) and not form_fields:
        #     term.printDebug( 'self.table_model: %s (type: %s)' %
        #                      (repr( self.table_model ), type( self.table_model )) )
        #     fld_list = self.table_model.get_default_attribute( 'fields' )
        #     term.printDebug( 'fld_list: %s' % repr( fld_list ) )
        if form_fields:
            form_fields = [ f for f in form_fields
                            if f not in exclude_fields ]
        # term.printDebug( 'form_fields: %s' % repr( form_fields ) )
#         term.printDebug( 'form_validators: %s' % repr( form_validators ) )

        if self.table_model and isinstance( self.table_model, DbBaseTable ) and not form_fields:
            # term.printDebug( 'self.table_model: %s (type: %s)' %
            #                  (repr( self.table_model ), type( self.table_model )) )
            form_fields = [ f for f in db[ self.get_table_name() ].fields
                            if f not in exclude_fields ]

        # term.printDebug( 'self.table_model: %s (type: %s)' %
        #                  (repr( self.table_model ), type( self.table_model )) )
        table = self.get_db_table()
        # term.printDebug( 'table: %s (type: %s)' %
        #                  (repr( table ), type( table )) )
        if self.table_model:
            dv_list = self.table_model.get_default_attribute( 'validators' )
            for field, value in dv_list.items():
                table[ field ].requires = value
#         term.printDebug( 'form_validators: %s' % repr( form_validators ) )
        for field, value in form_validators.items():
#             term.printDebug( 'field: %s; value: %s' %
#                              (repr( field ), repr( value )) )
            table[ field ].requires = value
#         for field in readonly_fields:
#             self.db[ self.table_model.table_name ][ field ].writable = False

#         term.printDebug( 'fields: %s' % repr( table.fields ) )
#         term.printDebug( 'table: %s' % repr( table ) )
#         term.printDebug( 'form_fields: %s' % repr( form_fields ) )
#         term.printDebug( 'record_id: %s' % repr( self.record_id ) )
        record = None
        if self.record_id:
            table_model = self.get_db_table()
            record = table_model[ self.record_id ]
#         term.printDebug( 'record: %s' % repr( record ) )
        form = SQLFORM( table,
                        record,
                        fields=form_fields,
                        deletable=deletable,
                        upload=upload,
                        showid=showid,
                        buttons=buttons,
                        extra_fields=extra_fields )
        if form_id:
            form[ '_id' ] = form_id
#         term.printDebug( 'form: %s' % form.xml() )
        from m16e.ui import ui_factory
        use_bootstrap_select = ui_factory.use_bootstrap_select()
        if use_bootstrap_select:
            for el in form.elements( 'select' ):
                # term.printDebug( 'el: %s' % repr( el ) )
                if len( el.components ) > htmlcommon.BOOTSTRAP_SELECTED_AUTO_THRESHOLD:
                    el[ '_data-none-selected-text' ] = htmlcommon.BOOTSTRAP_NONE_SELECTED_TEXT
                    el[ '_data-live-search' ] = 'true'
        if textarea_rows:
            for el in form.elements( 'textarea' ):
                el['_rows'] = textarea_rows
        for f in readonly_fields:
            fld_id = '#%s_%s' % ( self.table_model.table_name, f )
            el = form.element( fld_id )
            if el:
                if el.tag == 'select' or el[ '_type' ] == 'checkbox':
                    el['_disabled'] = 'disabled'
                else:
                    el['_readonly'] = 'readonly'
#                 term.printDebug( 'el: %s' % el.xml() )
            else:
                term.printLog( 'el id not in form: %s' % fld_id )
        pp_vars = self.get_pre_populated_vars()
        for pp in pp_vars:
            form.vars[ pp ] = pp_vars[ pp ]

        if not self.record_id:
            d_values = self.get_default_values()
            if d_values:
                for k in d_values:
                    form.vars[ k ] = d_values[ k ]
        table_name = self.get_table_name()
        placeholders = self.get_form_fields_placeholders()
#         term.printDebug( 'placeholders: %s' % repr( placeholders ) )
        for ph in placeholders:
            # term.printDebug( 'placeholders[ %s ]: %s' % (ph, placeholders[ ph ]) )
            el = form.element( '#%s_%s' % (table_name, ph) )
            if el:
                el['_placeholder'] = placeholders[ ph ]
            else:
                raise Exception( 'element not found: #%s_%s' % (table_name, ph) )

        # term.printDebug( 'form: %s' % form.xml() )
        self.append_org_fields( form )
        return form


    #------------------------------------------------------------------
    def update_record( self, upd ):
        # session = current.session
#        term.printDebug( 'updating #%d: %s' % (self.record_id, repr( upd ) ) )

        self.pre_upd( upd )
        upd = self.update_constant_values( upd )

#         term.printDebug( 'updating #%d: %s' % (self.record_id, repr( upd ) ) )
        if self.table_model:
            self.table_model.update_by_id( self.record_id, upd )
        else:
            db = self.db
            db( db[ self.get_table_name() ].id == self.record_id ).update( **upd )
        # session.flash = self.msg_record_updated
        self.post_upd( upd )
#        term.printDebug( 'updated #%d: %s' % (self.record_id, repr( upd ) ) )
        self.set_result( redirect=self.get_redirect_on_update(),
                         message=self.msg_record_updated )

    #------------------------------------------------------------------
    def pre_del( self ): pass
    def post_del( self ): pass
    def pre_ins( self, upd ): pass
    def post_ins( self, upd ): pass
    def pre_upd( self, upd ): pass
    def post_upd( self, upd ): pass

    @deprecated( replacement='one of pre_ins, pre_upd' )
    def pre_upd_ins( self, upd ): pass

    @deprecated( replacement='one of post_ins, post_upd' )
    def post_upd_ins( self, upd ): pass

    #------------------------------------------------------------------
    def do_insert_record( self, upd ):
        upd = self.update_constant_values( upd )
        if self.table_model:
            self.record_id = self.table_model.insert( upd )
        else:
            db = self.db
            self.record_id = db[ self.get_table_name() ].insert( **upd )
#         term.printLog( 'self.record_id: %s' % ( repr( self.record_id ) ) )


    #------------------------------------------------------------------
    def insert_record( self, upd ):
        session = current.session

        self.pre_ins( upd )
        if self.result.stop_execution:
            return

        self.do_insert_record( upd )

#         record_id = db[ self.table_model.table_name ].insert( **upd )
        session.flash = self.msg_record_created
        self.post_ins( upd  )
        self.set_result( redirect=self.get_redirect_on_insert(),
                         message=self.msg_record_created )


    #------------------------------------------------------------------
    def get_redirect_on_delete( self ):
        return URL( 'index' )

    #------------------------------------------------------------------
    def get_redirect_on_insert( self ):
        return URL( args=[ self.record_id ] )

    #------------------------------------------------------------------
    def get_redirect_on_update( self ):
        return URL( c=self.controller_name, f=self.function_name, args=[ self.record_id ] )

    #------------------------------------------------------------------
    def get_redirect_on_error( self ):
        return URL()

    #------------------------------------------------------------------
    def delete_record( self ):
        T = current.T
        session = current.session

        if self.table_model:
            self.table_model.delete( self.get_db_table().id == self.record_id )
        else:
            db = self.db
            db[ self.get_table_name() ].delete( self.get_db_table().id == self.record_id )
        self.record_id = None
        self.set_result( redirect=self.get_redirect_on_delete(), message=self.msg_record_deleted )

    #------------------------------------------------------------------
    def try_to_delete_record( self ):
        db = self.db
        response = current.response
        session = current.session
        T = current.T

        try:
            self.pre_del()
            self.delete_record()
            self.post_del()
        except DatabaseException as e:
            response.flash = str( e )
            term.printLog( 'DB EXCEPTION: %s' % str( e ) )
            self.set_result( stop_execution=True )
            db.rollback()
        except Error as e:
            t, v, tb = sys.exc_info()
            traceback.print_exception( t, v, tb )
            term.printLog( 'EXCEPTION\n  type: %s\n  exception: %s\n  pgerror: %s\n  pgcode: %s\n  args: %s' %
                           ( type( e ),
                             repr( e ),
                             e.pgerror,
                             e.pgcode,
                             e.args ) )
            if e.pgcode == errorcodes.FOREIGN_KEY_VIOLATION:
                p_detail = e.pgerror.split( 'DETAIL:' )[1].strip()
                sep = ' is still referenced from table '
                if sep in p_detail:
                    k = p_detail.split( sep )[0].split( '=' )[1].strip()[1:-1]

                    term.printLog( 'p_detail: %s' % repr( p_detail ) )
                    ref_table = p_detail.split( '"' )[1]
                    term.printLog( 'ref_table: %s' % repr( ref_table ) )
                    msg = T( 'Record referenced in other table' )
                    msg += ': ' + ref_table
                    self.fk_error = Storage( msg=msg,
                                             table=ref_table,
                                             key=k )
                    self.set_result( message=msg, stop_execution=True )
                    db.rollback()
                    return
            raise
        except:
            t, v, tb = sys.exc_info()
            traceback.print_exception( t, v, tb )
            raise
        # term.printDebug( 'result: %s' % repr( self.result ) )

    #------------------------------------------------------------------
    def process_form_action( self, form ):
        request = current.request
        response = current.response
        session = current.session
        T = current.T
        # term.printDebug( 'form.vars: ' + repr( form.vars ) )
        # if self.action == self.delete_action and form.deleted:
        #     self.try_to_delete_record()
        # el
        if self.action == self.submit_action:
            if form.deleted:
                self.try_to_delete_record()
            else:
                upd = self.get_changed_fields( form )
                # term.printDebug( 'upd: ' + repr( upd ) )
                if upd:
                    if self.record_id:
                        self.update_record( upd )
                    else:
                        self.insert_record( upd )
                else:
                    self.set_result( message=self.msg_nothing_to_update )
                    # response.flash = self.msg_nothing_to_update


    #------------------------------------------------------------------
    def process_form( self, form ):
        request = current.request
        response = current.response
        session = current.session
        T = current.T

#         term.printLog( 'action: ' + repr( self.action ) )
#         term.printDebug( 'request.vars: %s' % repr( request.vars ) )
#         term.printDebug( 'request.get_vars: %s' % repr( request.get_vars ) )
#         term.printDebug( 'request.post_vars: %s' % repr( request.post_vars ) )
#         term.printDebug( 'form.vars: %s' % repr( form.vars ) )
        if form.accepts( request.post_vars, session, dbio=False ):
            self.process_form_action( form )

        elif form.errors:
            term.printLog( 'form.errors: ' + repr( form.errors ) )
            term.printLog( 'form.errors: ' + str( form.errors ) )
            self.set_result( message=T( 'Form has errors' ) )
        self.errors = form.errors


    #------------------------------------------------------------------
    def fetch_record( self, fetch_id=False ):
        self.record = None
        if not self.record_id or fetch_id:
            self.fetch_record_id()
        if self.record_id:
            if self.table_model:
                self.record = self.table_model[ self.record_id ]
            else:
                db_table = self.get_db_table()
                if db_table:
                    self.record = db_table[ self.record_id ]
        return self.record


    #------------------------------------------------------------------
    def post_process_form( self, form ):
        # redirect = None

        self.fetch_record()
#         term.printDebug( 'record: %s' % repr( record ) )
        perms = Storage()
        perms.is_dev = is_in_group( K_ROLE_DEVELOPER )
        perms.is_admin = is_in_group( K_ROLE_ADMIN )
        perms.is_manager = is_in_group( K_ROLE_MANAGER )
        perms.is_editor = is_in_group( K_ROLE_EDITOR )
        perms.is_support = is_in_group( K_ROLE_SUPPORT )
        d = { self.get_table_name(): self.record,
              'form': form,
              'errors': self.errors or '',
              'view': self,
              'form_title': self.msg_form_title,
              'form_buttons': self.buttons,
              'perms': perms }
#         term.printDebug( 'result.dict: %s' % repr( d ) )
#         term.printDebug( 'result.redirect: %s' %
#                          ( repr( redirect ) ) )
        self.set_result( d )
        # term.printDebug( 'result.dict: %s' % repr( self.result.dict ) )
        # term.printDebug( 'result.redirect: %s' % ( repr( self.result.redirect ) ) )


    #------------------------------------------------------------------
    def fetch_record_id( self ):
        '''
        self.record_id = int( request.args( 0 ) or 0 )
        '''
        request = current.request
#         term.printLog( 'request.args: ' + repr( request.args ) )
        try:
            self.record_id = int( request.args( 0 ) )
        except:
            self.record_id = None


    #------------------------------------------------------------------
    def fetch_vars( self ):
        '''
        self.record_id = int( request.args( 0 ) or 0 )
        self.action = request.vars.action

        copies: request.vars.qk_* -> request.vars.qv_*
        '''
        request = current.request
#         term.printLog( 'request.args: ' + repr( request.args ) )
#         term.printLog( 'request.vars: ' + repr( request.vars ) )
        self.fetch_record_id()
        self.action = request.vars.get( KTF_ACTION )
        term.printLog( 'action: ' + repr( self.action ) )
        v_names = request.vars.keys()
        # set constants
        for v in v_names:
            if v.startswith( KQK_PREFIX ):
                value = request.vars[ v ]
                self.set_constant_value( v, value )
                v_name = v[ len( KQK_PREFIX ) : ]
                request.vars[ KQV_PREFIX + v_name ] = value
#         term.printDebug( 'record_id: %s\nconstants: %s' %
#                          ( repr( self.record_id ), repr( self.constant_values ) ) )
        self.next_c = request.vars.next_c or ''
        self.next_f = request.vars.next_f or ''
        self.next_args = request.vars.next_args or []


    #------------------------------------------------------------------
    def get_record_value( self, field_name ):
        if self.record:
            return self.record.get( field_name )
        return None


    #------------------------------------------------------------------
    def get_vars( self, prefix=None, field_names=[] ):
        request = current.request
#         term.printLog( 'request.args: ' + repr( request.args ) )
#         term.printLog( 'request.vars: ' + repr( request.vars ) )
        self.record_id = int( request.args( 0 ) or 0 )
        req_vars = Storage()
        for k in request.post_vars:
            if not prefix or prefix.startswith( prefix ):
                rq_k = rq_k = k[ len( prefix ) : ] if prefix else k
                if not field_names or rq_k in field_names:
                    req_vars[ rq_k ] = request.post_vars[ k ]
        for k in request.get_vars:
            if rq_k not in req_vars and ( not prefix or
                                          prefix.startswith( prefix ) ):
                rq_k = rq_k = k[ len( prefix ) : ] if prefix else k
                if not field_names or rq_k in field_names:
                    req_vars[ rq_k ] = request.get_vars[ k ]
        return req_vars

    #------------------------------------------------------------------
    def do_process( self ):
        request = current.request

        # term.printDebug( 'request.args: ' + repr( request.args ) )
        # term.printDebug( 'request.vars.keys: ' + repr( request.vars.keys() ) )
        self.fetch_vars()
        self.fetch_record()

        self.process_pre_validation_actions()
#         if self.result:
#             term.printDebug( 'result.redirect: %s\ndict.errors. %s' %
#                              ( repr( self.result.redirect ),
#                                repr( self.result.dict.get( 'errors' ) ) ) )
        if self.result.stop_execution and self.result.redirect:
            return self.result

        form = self.get_form()
        if not self.result.stop_execution:
            self.process_form( form )

        self.post_process_form( form )
#         term.printDebug( 'result: %s' % repr( result ) )
#         term.printDebug( 'self.response_message: %s' % repr( self.response_message ) )

        self.set_result( data=dict( page_js=self.get_page_js() ) )
        # term.printDebug( 'result: %s' % repr( self.result ) )

#         term.printDebug( 'result.redirect: %s\ndict. %s' %
#                          ( repr( self.result.redirect ),
#                            repr( self.result.dict.keys() ) ) )
#         term.printDebug( 'result.dict: %s' % repr( self.result.dict ) )
#         term.printDebug( 'self.response_message: %s' % repr( self.response_message ) )
        return self.result

    # #------------------------------------------------------------------
    # def process( self ):
    #     session = current.session
    #     response = current.response
    #     ret = None
    #     try:
    #         ret = self.do_process()
    #         # term.printDebug( 'result.redirect: %s' % repr( self.result.redirect ) )
    #         term.printDebug( 'self.response_message: %s' % repr( self.response_message ) )
    #         if self.response_message.msg:
    #             if self.response_message.msg_type == 'session':
    #                 session.flash = self.response_message.msg
    #             else:
    #                 response.flash = self.response_message.msg
    #     except:
    #         t, v, tb = sys.exc_info()
    #         traceback.print_exception( t, v, tb )
    #         raise
    #     return ret
