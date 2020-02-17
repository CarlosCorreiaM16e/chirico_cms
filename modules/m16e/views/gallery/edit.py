# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

import sys
import traceback
from psycopg2 import IntegrityError

from gluon import IS_IN_SET, IS_NULL_OR, IS_IN_DB
from m16e.db import db_tables
from gluon.compileapp import LOAD
from gluon.globals import current
from gluon.html import URL, A, BUTTON
from m16e import term
from m16e.db import attach_factory
from m16e.db.database import DBERR_FK_EXISTS
from m16e.kommon import ACT_SUBMIT, ATT_TYPE_IMAGES, UNIT_TYPE_SITE_ATTACHES
from m16e.ui import elements
from m16e.views.edit_base_view import BaseFormView


ACT_DUMP_TO_STATIC = 'dump_to_static'
ACT_RESIZE_IMG = 'act_resize_img'
ACT_CLONE_IMG = 'act_clone_img'

#------------------------------------------------------------------
class GalleryEditView( BaseFormView ):
    controller_name = 'gallery'
    function_name = 'edit'


    def __init__( self, db ):
        super( GalleryEditView, self ).__init__( db )
        self.table_model = db_tables.get_table_model( 'attach', db=db )

        self.next_c = None
        self.next_f = None
        self.next_args = None

        T = current.T
        self.msg_record_updated = T( 'Attach updated' )
        self.msg_record_created = T( 'Attach created' )

    #------------------------------------------------------------------
    def do_process( self ):
        return super( GalleryEditView, self ).do_process()


    def fetch_vars( self ):
        """
        page_id       = request.args( 0 )
        """
        super( GalleryEditView, self ).fetch_vars()
        request = current.request
        self.next_c = request.vars.next_c or ''
        self.next_f = request.vars.next_f or ''
        self.next_args = request.vars.next_args or []


    def process_pre_validation_actions( self ):
        request = current.request
        auth = current.auth
        T = current.T
        action = request.post_vars.action
        term.printLog( 'action: ' + repr( action ) )

        # if action == ACT_DUMP_TO_STATIC:
        #     attach_factory.file_dump_to_static( self.record_id )
        #     self.set_result( redirect=URL( c='gallery',
        #                                    f='edit',
        #                                    args=[ self.record_id ] ) )

        if action == ACT_RESIZE_IMG:
            # attach_id = int( request.vars.id )
            img_width = int( request.vars.img_width or 0 )
            if self.record.img_width == img_width:
                img_width = 0
            img_height = int( request.vars.img_height or 0 )
            if self.record.img_height == img_height:
                img_height = 0
            if img_width or img_height:
                term.printLog( 'copy image #%s ' + repr( self.record_id ) )
                new_attach_id = attach_factory.resize_image( self.record_id,
                                                             width=img_width,
                                                             db=self.db )
                self.set_result( redirect=URL( c=self.controller_name,
                                               f=self.function_name,
                                               args=[ new_attach_id ] ) )
            else:
                self.set_result( message=T( 'Must change either image width or height to resize' ) )

        if action == ACT_CLONE_IMG:
            img_width = int( request.vars.img_width or 0 )
            if self.record.img_width == img_width:
                img_width = 0
            img_height = int( request.vars.img_height or 0 )
            if self.record.img_height == img_height:
                img_height = 0
            if img_width or img_height:
                term.printLog( 'copy image #%s ' + repr( self.record_id ) )
                new_attach_id = attach_factory.copy_image( auth.user.id,
                                                           self.record_id,
                                                           new_width=img_width,
                                                           new_height=img_height,
                                                           insert_dim_in_name=True )
                self.set_result( redirect=URL( c=self.controller_name,
                                               f=self.function_name,
                                               args=[ new_attach_id ] ) )
            else:
                self.set_result( message=T( 'Must change either image width or height to resize' ) )


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
    #
    # def get_form( self,
    #               form_fields=[],
    #               form_validators={},
    #               deletable=True,
    #               textarea_rows=4,
    #               readonly_fields=[],
    #               upload=None,
    #               showid=True,
    #               buttons=[ ACT_SUBMIT ] ):
        T = current.T
        db = self.db

        term.printDebug( 'form_validators: %s' % repr( form_validators ) )
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

        if not form_fields:
            form_fields = [ f for f in db.attach.fields if not f in [ 'attached_file' ] ]
        ut_model = db_tables.get_table_model( 'unit_type', db=db )
        ut_list = ut_model.select( orderby='prefered_order' )
        ut_options = [ (ut.id, ut.name) for ut in ut_list ]
        form_validators[ 'unit_type_id' ] = IS_IN_SET( ut_options )
#         buttons = []
#         buttons.append( BUTTON( T( 'Submit' ),
#                                 _title=T( 'Submit form' ),
#                                 _name='action',
#                                 _value=ACT_SUBMIT,
#                                 _class='btn' ) )
#         if self.attach:
#             url = URL( c='gallery',
#                        f='ajax_resize',
#                        args=[ self.attach ] )
# #             onclick = '''ajax( '%(url)s', [ "img_width", "img_height" ], ":eval" );''' % { 'url': url }
#             buttons.append( BUTTON( T( 'Resize' ),
#                                     _title=T( 'Resize image' ),
#                                     _type='submit',
#                                     _name='action',
#                                     _value=ACT_RESIZE_IMG,
#                                     _class='btn' ) )
#
#             if self.attach.is_site_image:
#                 buttons.append( BUTTON( T( 'Dump to static' ),
#                                           _title=T( 'Dump to static filesytem' ),
#                                           _type='submit',
#                                           _name='action',
#                                           _value=ACT_DUMP_TO_STATIC,
#                                           _class='btn' ) )
#
#
        form = super( GalleryEditView, self ).get_form( form_fields=form_fields,
                                                        form_validators=form_validators,
                                                        deletable=deletable,
                                                        textarea_rows=textarea_rows,
                                                        readonly_fields=readonly_fields,
                                                        upload=URL( c='default', f='download' ),
                                                        buttons=buttons )
        if ut_list:
            ut = ut_list[ 0 ]
            form.vars.unit_type_id = ut.id
        at_model = db_tables.get_table_model( 'attach_type', db=db )
        at = at_model[ self.record.attach_type_id ]
        if self.record and at.meta_name == ATT_TYPE_IMAGES:
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
            super( GalleryEditView, self ).update_record( upd )
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
        ut_model = db_tables.get_table_model( 'unit_type', db=db )
        ut = ut_model[ request.vars.unit_type_id ]
        at_model = db_tables.get_table_model( 'attacch_type', db=db )
        at = at_model[ request.vars.attach_type_id ]
        is_site_image = (ut.meta_name == UNIT_TYPE_SITE_ATTACHES) and (at.meta_name == ATT_TYPE_IMAGES)

        self.record_id = attach_factory.add_attach( attached=request.vars.attached,
                                                    path=request.vars.path,
                                                    filename=request.vars.filename,
                                                    created_by=request.vars.created_by,
                                                    attach_type_id=request.vars.attach_type_id,
                                                    unit_type_id=request.vars.unit_type_id,
                                                    mime_type_id=request.vars.mime_type_id,
                                                    is_site_image=is_site_image,
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
        super( GalleryEditView, self ).post_process_form( form )
        js = ''
        if not self.next_c and self.record:
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
        self.set_result( dict( jscript=script ) )
        # self.result.dict.attach = self.record
        # self.result.dict.jscript = script


#     #------------------------------------------------------------------
#     def do_process( self ):
#         #------------------------------------------------------------------
#         request = current.request
#         response = current.response
#         session = current.session
#         T = current.T
#         db = self.db
#         auth = session.auth
#         redirect = None
#
# #         MimeTypeModel( db ).define_table()
#
#         ACT_DUMP_TO_STATIC = 'dump_to_static'
#         ACT_RESIZE_IMG = 'act_resize_img'
#
#         term.printLog( 'request.args: ' + repr( request.args ) )
#         term.printLog( 'request.vars: ' + repr( request.vars ) )
#         if request.post_vars:
#             term.printLog( 'request.post_vars: ' + repr( request.post_vars ) )
#
#         next_c = request.vars.next_c or ''
#         next_f = request.vars.next_f or ''
#         next_args = request.vars.next_args or []
#
#         attach_id = 0
#         attach = None
#         if request.args:                    # attach
#             attach_id = int( request.args( 0 ) )
#             if attach_id:
#                 attach = db.attach[ attach_id ]

#         term.printLog( 'attach_id: ' + repr( attach_id ) )
#
#         fields = [ f for f in db.attach.fields if not f in [ 'attached_file' ] ]
#
#         buttons = []
#         buttons.append( BUTTON( T( 'Submit' ),
#                                 _title=T( 'Submit form' ),
#                                 _name='action',
#                                 _value=ACT_SUBMIT,
#                                 _class='btn' ) )
#         if attach:
#             url = URL( c='gallery', f='ajax_resize', args=[ attach.id ] )
#             onclick = '''ajax( '%(url)s', [ "img_width", "img_height" ], ":eval" );''' % { 'url': url }
#             buttons.append( BUTTON( T( 'Resize' ),
#                                   _title=T( 'Resize image' ),
#                                   _type='submit',
#                                   _name='action',
#                                   _value=ACT_RESIZE_IMG,
#                                   _class='btn' ) )
#
#             if attach.is_site_image:
#                 buttons.append( BUTTON( T( 'Dump to static' ),
#                                           _title=T( 'Dump to static filesytem' ),
#                                           _type='submit',
#                                           _name='action',
#                                           _value=ACT_DUMP_TO_STATIC,
#                                           _class='btn' ) )
#
#         form = self.get_form( attach,
#                               form_fields=fields,
#                               deletable=True,
#                               upload=URL( c='default', f='download' ),
#                               buttons=buttons )
#         if attach and attach.is_site_image:
#                 td_chk = form.element( '#attach_is_site_image__row td.w2p_fw' )
#                 td_chk.append( ' - ' + T( 'File' ) + ': ')
#                 st_filename = attach_factory.is_file_in_static( attach.id )
#                 if st_filename:
#                     td_chk.append( st_filename )
#
#         action = request.post_vars.action
#         term.printLog( 'action: ' + repr( action ) )
#
#         if action == ACT_DUMP_TO_STATIC:
#             attach_factory.file_dump_to_static( attach_id )
#             redirect = URL( c='gallery', f='edit', args = [ attach_id ] )
#             return Storage( dict=dict(), redirect=redirect )
#
#         if action == ACT_RESIZE_IMG:
#             attach_id = int( request.vars.id )
#             img_width = int( request.vars.img_width or 0 )
#             img_height = int( request.vars.img_height or 0 )
#             term.printLog( 'copy image #%s ' + repr( attach_id ) )
#             new_attach_id = attach_factory.copy_image( auth.user.id,
#                                                        attach_id,
#                                                        new_width=img_width,
#                                                        new_height=img_height,
#                                                        insert_dim_in_name=True )
#             redirect = URL( c='gallery', f='edit', args = [ new_attach_id ] )
#             return Storage( dict=dict(), redirect=redirect )
#
#         msg = ''
#         try:
#             if form.accepts( request.vars, session, dbio=False ):
#                 term.printDebug( 'form.vars: %s' % ( repr( form.vars) ) )
#                 if action == ACT_SUBMIT:
#                     if request.vars.delete_this_record:
#                         attach_factory.delete_from_static( attach.id )
#                         self.table_model.delete_by_id( attach.id )
#                         session.flash = T( 'Attach deleted' )
#                         redirect = URL( c='gallery', f='index' )
#                     else:
#                         upd = htmlcommon.getChangedFields( form.vars, request.post_vars, db[ self.table_model.table_name ] )
#                         if upd:
#                             term.printLog( 'upd: ' + repr( upd ) )
#                             if attach:
#                                 self.table_model.update_by_id( attach.id, upd )
#                                 session.flash = T( 'Attach updated' )
#                             else:
#                                 session.flash = T( 'Attach created' )
#                                 attach_id = attach_factory.add_attach( attached=request.vars.attached,
#                                                                        path=request.vars.path,
#                                                                        filename=request.vars.filename,
#                                                                        created_by=request.vars.created_by,
#                                                                        attach_type_id=request.vars.attach_type_id,
#                                                                        unit_type_id=request.vars.unit_type_id,
#                                                                        mime_type_id=request.vars.mime_type_id,
#                                                                        is_site_image=request.vars.is_site_image,
#                                                                        short_description=request.vars.short_description,
#                                                                        long_description=request.vars.long_description,
#                                                                        created_on=request.vars.created_on,
#                                                                        img_width=request.vars.img_width,
#                                                                        img_height=request.vars.img_height,
#                                                                        org_attach_id=request.vars.org_attach_id )
#                             attach_factory.file_dump_to_static( attach_id, db=db )
#
#                             if next_c:
#                                 d_vars = { 'next_c': next_c,
#                                            'next_f': next_f,
#                                            'next_args': next_args }
#                                 redirect = URL( c=next_c, f=next_f, args=next_args, vars=d_vars )
#
# #                 if request.vars.delete_this_record:
# #                     session.flash = T( 'Attach deleted' )
# #                     redirect = URL( c='gallery', f='index' )
# #                 elif attach:
# #                     session.flash = T( 'Attach updated' )
# #                 else:
# #                     term.printDebug( 'form.vars: %s' % ( repr( form.vars) ) )
# #                     session.flash = T( 'Attach created' )
# #                     if next_c:
# #                         d_vars = { 'next_c': next_c,
# #                                    'next_f': next_f,
# #                                    'next_args': next_args }
# #                         redirect = URL( c=next_c, f=next_f, args=next_args, vars=d_vars )
#
#                 if not redirect:
#                     redirect = URL( c='gallery', f='edit', args = [ attach_id ] )
#
#             elif form.errors:
#                 term.printLog( 'form.errors: ' + repr( form.errors ) )
#                 response.flash = T( 'Form has errors' )
#
#             elif attach:
#                 response.flash = T( 'Nothing to update' )
#         except IntegrityError as e:
#             t, v, tb = sys.exc_info()
#             traceback.print_exception( t, v, tb )
#             term.printDebug( 'exception type: %s' % type( e ) )
#             term.printDebug( '  exception: %s' % repr( e ) )
#             term.printDebug( '    pgerror: %s' % e.pgerror )
#             term.printDebug( '    pgcode: %s' % e.pgcode )
#             term.printDebug( '    args: %s' % repr( e.args ) )
# #                 term.printDebug( '    diag: %s' % repr( e.diag ) )
#             db.rollback()
#             if e.pgcode == DBERR_FK_EXISTS:
#                 T.lazy = False
#                 msg = T( 'Integrity violation' )
#                 p_detail = e.pgerror.split( 'DETAIL:' )[1].strip()
#                 if 'is still referenced from table ' in p_detail:
#                     p_table = p_detail.split( '"' )[1]
#                     msg = T( 'record(s) referenced in other table(s)' )
#                     ref_tables = []
#                     if p_table == 'qo_attach':
#                         ref_tables.append( T( 'question option attach' ) )
#                     elif p_table == 'block':
#                         ref_tables.append( T( 'block' ) )
#                     if ref_tables:
#                         msg += ': %s' % ', '.join( ref_tables )
#                 T.lazy = True
#             term.printDebug( msg )
#             response.flash = msg
#
# #             response.js = '''
# #                 jQuery( '.flash' ).css( 'background-color', '#A85454' );
# #                 '''
#
#         div = DIV( form )
#
#         js = ''
#         if not next_c and attach:
#             i = I( _class='glyphicon glyphicon-plus glyphicon-white' )
#             url = URL( c='unit_type', f='edit', args=[0],
#                        vars={ 'next_c': 'gallery',
#                               'next_f': 'edit',
#                               'next_args': [ attach.id ] } )
#             bt_add_ut = A( i, _href=url, _class='dark_bg', _style='margin-left: 5px;' )
#             url = URL( c='attach_type', f='edit', args=[0],
#                        vars={ 'next_c': 'gallery',
#                               'next_f': 'edit',
#                               'next_args': [ attach.id ] } )
#             bt_add_at = A( i, _href=url, _class='dark_bg', _style='margin-left: 5px;' )
#             js += '''
#                 var w = jQuery( '#attach_attach_type_id' ).width() - 50;
#                 window.console && console.log( "width: " + w );
#                 if( w > 160 )
#                 {
#                     jQuery( '#attach_attach_type_id' ).width( w );
#                     jQuery( '#attach_unit_type_id' ).width( w );
#                 }
#                 jQuery( '#attach_attach_type_id' ).parent().append( '%(add_at)s' );
#                 jQuery( '#attach_unit_type_id' ).parent().append( '%(add_ut)s' );
#             ''' % { 'add_at': bt_add_at.xml(), 'add_ut': bt_add_ut.xml() }
#         term.printDebug( 'js: %s' % js )
#         if js:
#             script = js
#         else:
#             script = ''
#         return Storage( dict=dict( attach=attach,
#                                    form=div,
#                                    message=msg,
#                                    jscript=script ),
#                         redirect=redirect )


