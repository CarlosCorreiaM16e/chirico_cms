# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

import sys
import traceback
from psycopg2 import IntegrityError

from m16e.db import db_tables
from gluon.globals import current
from gluon.html import URL, A, BUTTON
from m16e import term
from m16e.db import attach_factory
from m16e.db.database import DBERR_FK_EXISTS
from m16e.kommon import ACT_SUBMIT
from m16e.ui import elements
from m16e.views.edit_base_view import BaseFormView

ACT_DUMP_TO_STATIC = 'dump_to_static'
ACT_RESIZE_IMG = 'act_resize_img'

#------------------------------------------------------------------
class MediaEditView( BaseFormView ):
    def __init__( self, db ):
        super( MediaEditView, self ).__init__( db )
        self.table_model = db_tables.get_table_model( 'attach', db=db )
        self.attach = None

        self.next_c = None
        self.next_f = None
        self.next_args = None

        T = current.T
        self.msg_record_updated = T( 'Attach updated' )
        self.msg_record_created = T( 'Attach created' )

    #------------------------------------------------------------------
    def do_process( self ):
        return super( MediaEditView, self ).do_process()

    #------------------------------------------------------------------
    def fetch_vars( self ):
        """
        page_id       = request.args( 0 )
        """
        request = current.request
        self.record_id = int( request.args( 0 ) or 0 )
        self.attach = self.table_model[ self.record_id ]

        self.next_c = request.vars.next_c or ''
        self.next_f = request.vars.next_f or ''
        self.next_args = request.vars.next_args or []

    #------------------------------------------------------------------
    def process_pre_validation_actions( self ):
        request = current.request
        auth = current.auth

        action = request.post_vars.action
        term.printLog( 'action: ' + repr( action ) )

        if action == ACT_DUMP_TO_STATIC:
            attach_factory.file_dump_to_static( self.record_id )
            self.set_result( redirect=URL( c='gallery',
                                           f='edit',
                                           args=[ self.record_id ] ) )

        elif action == ACT_RESIZE_IMG:
            attach_id = int( request.vars.id )
            img_width = int( request.vars.img_width or 0 )
            img_height = int( request.vars.img_height or 0 )
            term.printLog( 'copy image #%s ' + repr( attach_id ) )
            new_attach_id = attach_factory.copy_image( auth.user.id,
                                                       attach_id,
                                                       new_width=img_width,
                                                       new_height=img_height,
                                                       insert_dim_in_name=True )
            self.set_result( redirect=URL( c='gallery',
                                           f='edit',
                                           args = [ new_attach_id ] ) )

    #------------------------------------------------------------------
    def get_form_fields( self ):
        self.form_fields = [ 'path',
                             'filename',
                             'short_description',
                             'long_description',
                             'attached',
                             'created_on',
                             'created_by',
                             'unit_type_id',
                             'is_site_image',
                             'img_width',
                             'img_height',
                             'attach_type_id',
                             'org_attach_id' ]
        return self.form_fields

    #------------------------------------------------------------------
    def get_form( self,
                  form_fields=[],
                  form_validators={},
                  deletable=True,
                  textarea_rows=4,
                  readonly_fields=[],
                  upload=None,
                  showid=True,
                  buttons=[ ACT_SUBMIT ] ):
        T = current.T
        db = self.db

        term.printDebug( 'form_validators: %s' % repr( form_validators ) )
        if not form_fields:
            form_fields = [ f for f in db.attach.fields if not f in [ 'attached_file' ] ]

        buttons = []
        buttons.append( BUTTON( T( 'Submit' ),
                                _title=T( 'Submit form' ),
                                _name='action',
                                _value=ACT_SUBMIT,
                                _class='btn' ) )
        if self.attach:
            url = URL( c='gallery',
                       f='ajax_resize',
                       args=[ self.attach ] )
#             onclick = '''ajax( '%(url)s', [ "img_width", "img_height" ], ":eval" );''' % { 'url': url }
            buttons.append( BUTTON( T( 'Resize' ),
                                    _title=T( 'Resize image' ),
                                    _type='submit',
                                    _name='action',
                                    _value=ACT_RESIZE_IMG,
                                    _class='btn' ) )

            if self.attach.is_site_image:
                buttons.append( BUTTON( T( 'Dump to static' ),
                                          _title=T( 'Dump to static filesytem' ),
                                          _type='submit',
                                          _name='action',
                                          _value=ACT_DUMP_TO_STATIC,
                                          _class='btn' ) )


        form = super( MediaEditView, self ).get_form( form_fields=form_fields,
                                                        form_validators=form_validators,
                                                        deletable=deletable,
                                                        textarea_rows=textarea_rows,
                                                        readonly_fields=readonly_fields,
                                                        upload=URL( c='default', f='download' ),
                                                        buttons=buttons )
        if self.attach and self.attach.is_site_image:
            td_chk = form.element( '#attach_is_site_image__row td.w2p_fw' )
            td_chk.append( ' - ' + T( 'File' ) + ': ')
            st_filename = attach_factory.is_file_in_static( self.record_id )
            if st_filename:
                td_chk.append( st_filename )

        return form

    #------------------------------------------------------------------
    def update_record( self, upd ):
        response = current.response
        T = current.T
        db = self.db
        term.printDebug( 'upd: %s' % repr( upd ) )
        try:
            super( MediaEditView, self ).update_record( upd )
        except IntegrityError as e:
            t, v, tb = sys.exc_info()
            traceback.print_exception( t, v, tb )
            term.printDebug( 'exception type: %s' % type( e ) )
            term.printDebug( '  exception: %s' % repr( e ) )
            term.printDebug( '    pgerror: %s' % e.pgerror )
            term.printDebug( '    pgcode: %s' % e.pgcode )
            term.printDebug( '    args: %s' % repr( e.args ) )
#                 term.printDebug( '    diag: %s' % repr( e.diag ) )
            db.rollback()
            if e.pgcode == DBERR_FK_EXISTS:
                T.lazy = False
                self.errors = T( 'Integrity violation' )
                p_detail = e.pgerror.split( 'DETAIL:' )[1].strip()
                if 'is still referenced from table ' in p_detail:
                    p_table = p_detail.split( '"' )[1]
                    self.errors = T( 'record(s) referenced in other table(s)' )
                    ref_tables = []
                    if p_table == 'qo_attach':
                        ref_tables.append( T( 'question option attach' ) )
                    elif p_table == 'block':
                        ref_tables.append( T( 'block' ) )
                    if ref_tables:
                        self.errors += ': %s' % ', '.join( ref_tables )
                T.lazy = True
            term.printDebug( self.errors )
            response.flash = self.errors

    #------------------------------------------------------------------
    def delete_record( self, upd ):
        response = current.response
        T = current.T
        session = current.session
        db = self.db
        try:
            attach_factory.delete_from_static( self.record_id )
            self.table_model.delete_by_id( self.record_id )
            session.flash = T( 'Attach deleted' )
            self.set_result( redirect=URL( c='gallery', f='index' ) )
        except IntegrityError as e:
            t, v, tb = sys.exc_info()
            traceback.print_exception( t, v, tb )
            term.printDebug( 'exception type: %s' % type( e ) )
            term.printDebug( '  exception: %s' % repr( e ) )
            term.printDebug( '    pgerror: %s' % e.pgerror )
            term.printDebug( '    pgcode: %s' % e.pgcode )
            term.printDebug( '    args: %s' % repr( e.args ) )
#                 term.printDebug( '    diag: %s' % repr( e.diag ) )
            db.rollback()
            if e.pgcode == DBERR_FK_EXISTS:
                T.lazy = False
                self.errors = T( 'Integrity violation' )
                p_detail = e.pgerror.split( 'DETAIL:' )[1].strip()
                if 'is still referenced from table ' in p_detail:
                    p_table = p_detail.split( '"' )[1]
                    self.errors = T( 'record(s) referenced in other table(s)' )
                    ref_tables = []
                    if p_table == 'qo_attach':
                        ref_tables.append( T( 'question option attach' ) )
                    elif p_table == 'block':
                        ref_tables.append( T( 'block' ) )
                    if ref_tables:
                        self.errors += ': %s' % ', '.join( ref_tables )
                T.lazy = True
            term.printDebug( self.errors )
            response.flash = self.errors

    #------------------------------------------------------------------
    def insert_record( self, upd ):
        request = current.request
        db = self.db
        self.record_id = attach_factory.add_attach( attached=request.vars.attached,
                                                    path=request.vars.path,
                                                    filename=request.vars.filename,
                                                    created_by=request.vars.created_by,
                                                    attach_type_id=request.vars.attach_type_id,
                                                    unit_type_id=request.vars.unit_type_id,
                                                    mime_type_id=request.vars.mime_type_id,
                                                    is_site_image=request.vars.is_site_image,
                                                    short_description=request.vars.short_description,
                                                    long_description=request.vars.long_description,
                                                    created_on=request.vars.created_on,
                                                    img_width=request.vars.img_width,
                                                    img_height=request.vars.img_height,
                                                    org_attach_id=request.vars.org_attach_id )
        attach_factory.file_dump_to_static( self.record_id, db=db )

        if self.next_c:
            d_vars = { 'next_c': self.next_c,
                       'next_f': self.next_f,
                       'next_args': self.next_args }
            self.set_result( redirect=URL( c=self.next_c,
                                           f=self.next_f,
                                           args=self.next_args,
                                           vars=d_vars ) )

    #------------------------------------------------------------------
    def post_process_form( self, form ):
        db = self.db
        super( MediaEditView, self ).post_process_form( form )
        js = ''
        if not self.next_c and self.attach:
            i = elements.get_bootstrap_icon( 'plus' )
            url = URL( c='unit_type', f='edit', args=[0],
                       vars={ 'next_c': 'gallery',
                              'next_f': 'edit',
                              'next_args': [ self.record_id ] } )
            bt_add_ut = A( i, _href=url, _class='dark_bg', _style='margin-left: 5px;' )
            url = URL( c='attach_type', f='edit', args=[0],
                       vars={ 'next_c': 'gallery',
                              'next_f': 'edit',
                              'next_args': [ self.record_id ] } )
            bt_add_at = A( i, _href=url, _class='dark_bg', _style='margin-left: 5px;' )
            js += '''
                var w = jQuery( '#attach_attach_type_id' ).width() - 50;
                window.console && console.log( "width: " + w );
                if( w > 160 )
                {
                    jQuery( '#attach_attach_type_id' ).width( w );
                    jQuery( '#attach_unit_type_id' ).width( w );
                }
                jQuery( '#attach_attach_type_id' ).parent().append( '%(add_at)s' );
                jQuery( '#attach_unit_type_id' ).parent().append( '%(add_ut)s' );
            ''' % { 'add_at': bt_add_at.xml(), 'add_ut': bt_add_ut.xml() }
        term.printDebug( 'js: %s' % js )
        if js:
            script = js
        else:
            script = ''
        self.result.dict.attach = self.attach
        self.result.dict.jscript = script



