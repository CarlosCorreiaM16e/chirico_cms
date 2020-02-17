# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
import os
import sys
import traceback
from psycopg2 import IntegrityError

from belmiro.app.k import CFG_IMG_SIZE_SMALL, CFG_IMG_SIZE_LARGE, CFG_IMG_SIZE_MEDIUM
from chirico.db import block_factory
from gluon import IS_IN_SET, SPAN, B
from gluon.storage import Storage
from m16e.db import db_tables
from gluon.globals import current
from gluon.html import URL, A, BUTTON
from m16e import term
from m16e.db import attach_factory
from m16e.db.database import DBERR_FK_EXISTS
from m16e.files import fileutils
from m16e.kommon import ACT_SUBMIT, ATT_TYPE_IMAGES, UNIT_TYPE_SITE_ATTACHES
from m16e.ui import elements
from m16e.views.edit_base_view import BaseFormView

ACT_CLONE_IMG = 'act_clone_img'
ACT_DUMP_TO_STATIC = 'dump_to_static'
ACT_RESIZE_IMG = 'act_resize_img'
ACT_SANITIZE_FILENAME = 'act_sanitize_filename'


class CmsGalleryEditImageView( BaseFormView ):
    controller_name = 'gallery'
    function_name = 'edit'


    def __init__( self, db ):
        super( CmsGalleryEditImageView, self ).__init__( db )
        self.table_model = db_tables.get_table_model( 'attach', db=db )

        T = current.T
        self.msg_record_updated = T( 'Attach updated' )
        self.msg_record_created = T( 'Attach created' )
        self.old_path = None
        self.old_filename = None
        self.old_pathname = None
        self.old_url = None


    def do_process( self ):
        return super( CmsGalleryEditImageView, self ).do_process()


    def fetch_record( self, fetch_id=False ):
        super( CmsGalleryEditImageView, self ).fetch_record( fetch_id )
        if self.record:
            self.old_path = self.record.path
            self.old_filename = self.record.filename
            self.old_url = attach_factory.get_url( self.record_id, db=self.db )
            u_parts = self.old_url.split( '/' )
            if u_parts[0] == '' and u_parts[1] == current.app_name:
                del( u_parts[1] )
                del( u_parts[1] )
                self.old_url = '/'.join( u_parts )
            self.old_pathname = os.path.join( attach_factory.get_rel_path_from_server_app( self.record, db=self.db ),
                                              self.record.filename )


    def process_pre_validation_actions( self ):
        T = current.T
        request = current.request
        auth = current.auth
        db = self.db
        term.printLog( 'action: ' + repr( self.action ) )

        if self.action == self.delete_action:
            self.try_to_delete_record()
            if self.next_c:
                url = URL( c=self.next_c, f=self.next_f, args=self.next_args )
            else:
                url = URL( c=self.controller_name, f='list_images' )
            return self.set_result( redirect=url,
                                    message=T( 'Image deleted' ) )

        if self.action == ACT_CLONE_IMG:
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
                                                           new_short_description=self.record.short_description,
                                                           insert_dim_in_name=True,
                                                           dump_to_static=True )
                return self.set_result( redirect=URL( c=self.controller_name,
                                                      f=self.function_name,
                                                      args=[ new_attach_id ] ) )
            else:
                return self.set_result( message=T( 'Must change either image width or height to clone' ) )

        if self.action == ACT_DUMP_TO_STATIC:
            attach_factory.file_dump_to_static( self.record_id )
            self.set_result( redirect=URL( c='gallery',
                                           f='edit',
                                           args=[ self.record_id ] ) )


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
                             'mime_type_id',
                             'attach_type_id',
                             'org_attach_id' ]
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
        if buttons is None:
            buttons = [ ACT_SUBMIT ]
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
        term.printDebug( 'form_validators: %s' % repr( form_validators ) )
        if not form_fields:
            form_fields = [ f for f in db.attach.fields if not f in [ 'attached_file' ] ]
        ut_model = db_tables.get_table_model( 'unit_type', db=db )
        ut_list = ut_model.select( orderby='preferred_order' )
        ut_options = [ (ut.id, ut.name) for ut in ut_list ]
        form_validators[ 'unit_type_id' ] = IS_IN_SET( ut_options )

        form = super( CmsGalleryEditImageView, self ).get_form( form_fields=form_fields,
                                                             form_validators=form_validators,
                                                             deletable=deletable,
                                                             textarea_rows=textarea_rows,
                                                             readonly_fields=readonly_fields,
                                                             upload=URL( c='default', f='download' ),
                                                             buttons=buttons )
        if ut_list:
            ut = ut_list[ 0 ]
            form.vars.unit_type_id = ut.id
        if self.record and self.record.attach_type_id:
            at_model = db_tables.get_table_model( 'attach_type', db=db )
            at = at_model[ self.record.attach_type_id ]
            if at.meta_name == ATT_TYPE_IMAGES:
                td_chk = form.element( '#attach_is_site_image__row td.w2p_fw' )
                if td_chk:
                    td_chk.append( ' - ' + T( 'File' ) + ': ' )
                    st_filename = attach_factory.is_file_in_static( self.record_id )
                    if st_filename:
                        td_chk.append( st_filename )

        return form


    def pre_ins( self, upd ):
        super( CmsGalleryEditImageView, self ).pre_ins( upd )
        db = self.db
        request = current.request
        T = current.T
        term.printDebug( 'upd: %s' % repr( upd ) )
        ut_model = db_tables.get_table_model( 'unit_type', db=db )
        ut = ut_model[ request.vars.unit_type_id ]
        at_model = db_tables.get_table_model( 'attacch_type', db=db )
        at = at_model[ request.vars.attach_type_id ]
        upd[ 'is_site_image' ] = (ut.meta_name == UNIT_TYPE_SITE_ATTACHES) and (at.meta_name == ATT_TYPE_IMAGES)
        if upd.filename:
            upd.filename = fileutils.filename_sanitize( upd.filename )
            # self.old_pathname = attach_factory.file_dump( self.record_id, db=db )


    def pre_upd( self, upd ):
        super( CmsGalleryEditImageView, self ).pre_upd( upd )
        db = self.db
        request = current.request
        T = current.T
        term.printDebug( 'upd: %s' % repr( upd ) )
        if upd.filename:
            upd.filename = fileutils.filename_sanitize( upd.filename )
        if 'attached' in upd:
            if upd.attached:
                upd.attached_file = upd.attached.file.read()
            else:
                del( upd.attached )
            # self.old_pathname = attach_factory.file_dump( self.record_id, db=db )
        # if self.action == ACT_RESIZE_IMG:
        #     self.old_pathname = attach_factory.file_dump_to_static( self.record_id, db=db )
        if self.action == ACT_RESIZE_IMG:
            img_width = upd.img_width
            attach_factory.resize_image( self.record_id,
                                         width=img_width,
                                         new_filename=upd.filename or self.old_filename,
                                         db=db )
            self.set_result( message=T( 'Image resized' ) )


    def post_upd( self, upd ):
        super( CmsGalleryEditImageView, self ).post_upd( upd )
        db = self.db
        T = current.T
        # rename static file if needed
        if 'filename' in upd or 'path' in upd:
            attach_factory.file_dump_to_static( self.record_id, db=db )
            b_model = db_tables.get_table_model( 'block', db=db )
            path = os.path.join( attach_factory.get_rel_path_from_app_static( attach_id=self.record_id, db=db ),
                                 self.old_path )
            blocks = block_factory.get_blocks_with_image( self.old_url,
                                                          db=db )
            for block in blocks:
                new_url = attach_factory.get_url( self.record_id, db=db )
                u = Storage()
                for fld in ('body', 'body_en'):
                    if self.old_url in block[ fld ]:
                        u[ fld ] = block[ fld ].replace( self.old_url, new_url )
                if u:
                    b_model.update_by_id( block.id, u )



    # def update_record( self, upd ):
    #     response = current.response
    #     T = current.T
    #     db = self.db
    #     term.printDebug( 'upd: %s' % repr( upd ) )
    #     try:
    #         super( CmsGalleryEditImageView, self ).update_record( upd )
    #     except IntegrityError as e:
    #         t, v, tb = sys.exc_info()
    #         traceback.print_exception( t, v, tb )
    #         term.printDebug( 'exception type: %s' % type( e ) )
    #         term.printDebug( '  exception: %s' % repr( e ) )
    #         term.printDebug( '    pgerror: %s' % e.pgerror )
    #         term.printDebug( '    pgcode: %s' % e.pgcode )
    #         term.printDebug( '    args: %s' % repr( e.args ) )
    #         #                 term.printDebug( '    diag: %s' % repr( e.diag ) )
    #         db.rollback()
    #         if e.pgcode == DBERR_FK_EXISTS:
    #             T.lazy = False
    #             self.errors = T( 'Integrity violation' )
    #             p_detail = e.pgerror.split( 'DETAIL:' )[ 1 ].strip()
    #             if 'is still referenced from table ' in p_detail:
    #                 p_table = p_detail.split( '"' )[ 1 ]
    #                 self.errors = T( 'record(s) referenced in other table(s)' )
    #                 ref_tables = [ ]
    #                 if p_table == 'qo_attach':
    #                     ref_tables.append( T( 'question option attach' ) )
    #                 elif p_table == 'block':
    #                     ref_tables.append( T( 'block' ) )
    #                 if ref_tables:
    #                     self.errors += ': %s' % ', '.join( ref_tables )
    #             T.lazy = True
    #         term.printDebug( self.errors )
    #         self.set_result( message=self.errors )
    #

    def delete_record( self ):
        response = current.response
        T = current.T
        session = current.session
        db = self.db
        try:
            attach_factory.delete_attach( self.record_id, db=db )
            # self.table_model.delete_by_id( self.record_id )
            # session.flash = T( 'Attach deleted' )
            # self.set_result( redirect=URL( c='gallery', f='index' ), message=T( 'Attach deleted' ) )
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
                p_detail = e.pgerror.split( 'DETAIL:' )[ 1 ].strip()
                if 'is still referenced from table ' in p_detail:
                    p_table = p_detail.split( '"' )[ 1 ]
                    self.errors = T( 'record(s) referenced in other table(s)' )
                    ref_tables = [ ]
                    if p_table == 'qo_attach':
                        ref_tables.append( T( 'question option attach' ) )
                    elif p_table == 'block':
                        ref_tables.append( T( 'block' ) )
                    if ref_tables:
                        self.errors += ': %s' % ', '.join( ref_tables )
                T.lazy = True
            term.printDebug( self.errors )
            response.flash = self.errors


    def insert_record( self, upd ):
        db = self.db
        T = current.T
        term.printDebug( 'upd: %s' % repr( upd ) )
        self.record_id = attach_factory.add_attach( attached=upd.attached,
                                                    path=upd.path,
                                                    filename=upd.filename,
                                                    created_by=upd.created_by,
                                                    attach_type_id=upd.attach_type_id,
                                                    unit_type_id=upd.unit_type_id,
                                                    mime_type_id=upd.mime_type_id,
                                                    is_site_image=upd.is_site_image,
                                                    short_description=upd.short_description,
                                                    long_description=upd.long_description,
                                                    img_width=upd.img_width,
                                                    img_height=upd.img_height,
                                                    org_attach_id=upd.org_attach_id,
                                                    dump_to_static=True )
        # attach_factory.file_dump_to_static( self.record_id, db=db )
        msg = T( 'Image created' )
        if self.next_c:
            d_vars = { 'next_c': self.next_c,
                       'next_f': self.next_f,
                       'next_args': self.next_args }
            self.set_result( redirect=URL( c=self.next_c,
                                           f=self.next_f,
                                           args=self.next_args,
                                           vars=d_vars ),
                             message=msg )
        else:
            self.set_result( redirect=self.get_redirect_on_insert(), message=msg )


    def get_changed_fields( self, form, field_prefix='', get_all=False, db_table=None ):
        upd = super( CmsGalleryEditImageView, self ).get_changed_fields( form,
                                                                         field_prefix=field_prefix,
                                                                         get_all=get_all,
                                                                         db_table=db_table )
        if 'attached' in upd and not upd.attached:
            del( upd.attached )
            if not upd:
                return Storage()
        return upd


    def process_form_action( self, form ):
        # super( GalleryEditImageView, self ).process_form_action( form )
        request = current.request
        auth = current.auth
        session = current.session
        T = current.T
        # term.printDebug( 'form.vars: ' + repr( form.vars ) )
        db = self.db
        if self.action in (self.submit_action, ACT_RESIZE_IMG, ACT_SANITIZE_FILENAME, ACT_DUMP_TO_STATIC):
            upd = self.get_changed_fields( form )
            # term.printDebug( 'upd: ' + repr( upd ) )
            if self.action in (ACT_SANITIZE_FILENAME, ACT_DUMP_TO_STATIC) or 'filename' in upd:
                filename = upd.filename or self.record.filename
                s_filename = fileutils.filename_sanitize( filename )
                if filename != s_filename:
                    upd.filename = s_filename
            if upd:
                if self.record_id:
                    if upd.attached__delete and self.action != ACT_RESIZE_IMG:
                        attach_factory.delete_from_static( self.record_id, db=db )
                    self.update_record( upd )
                    # if self.action == ACT_RESIZE_IMG:
                    #     img_width = int( request.vars.img_width )
                    #     new_attach_id = attach_factory.resize_image( self.record_id,
                    #                                                  width=img_width,
                    #                                                  db=db )
                    #     return self.set_result( redirect=URL( c='gallery',
                    #                                           f='edit',
                    #                                           args=[ new_attach_id ] ),
                    #                             message=T( 'Image resized' ) )

                else:
                    self.insert_record( upd )
            else:
                self.set_result( message=self.msg_nothing_to_update )

                # response.flash = self.msg_nothing_to_update


    # ------------------------------------------------------------------
    def post_process_form( self, form ):
        db = self.db
        super( CmsGalleryEditImageView, self ).post_process_form( form )
        js = ''
        if not self.next_c and self.record:
            i = elements.get_bootstrap_icon( 'plus' )
            url = URL( c='unit_type', f='edit', args=[ 0 ],
                       vars={ 'next_c': 'gallery',
                              'next_f': 'edit',
                              'next_args': [ self.record_id ] } )
            bt_add_ut = A( i, _href=url, _class='dark_bg', _style='margin-left: 5px;' )
            url = URL( c='attach_type', f='edit', args=[ 0 ],
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
        T = current.T

        def get_new_heigth( base_w, base_h, new_w ):
            ratio = float( new_w ) / float( base_w )
            if ratio < 1.0:
                return int( base_h * ratio )
            return base_h

        children = []
        span_resize = ''
        if self.record:
            ac = current.app_config
            onclick = '''
                jQuery( '#attach_img_width' ).val( '%(w)s' );
                jQuery( '#attach_img_height' ).val( '%(h)s' );
                var farr = jQuery( '#attach_filename' ).val().split( '.' );
                var lidx = farr.length - 2;
                var sizes = [ %(l)s, %(m)s, %(s)s ];
                for ( let i = 0; i < sizes.length; i++ ) {
                    var ws = '-w' + sizes[i];
                    farr[ lidx ] = farr[ lidx ].split( ws )[0];
                }
                farr[ lidx ] += '-%(w)sx%(h)s';
                jQuery( '#attach_filename' ).val( farr.join( '.' ) );
                '''
            span_resize = SPAN( '[ ' )
            data = Storage( l=ac.take( CFG_IMG_SIZE_LARGE ),
                            m=ac.take( CFG_IMG_SIZE_MEDIUM ),
                            s=ac.take( CFG_IMG_SIZE_SMALL ) )
            data.w = ac.take( CFG_IMG_SIZE_SMALL )
            data.h = get_new_heigth( self.record.img_width, self.record.img_height, data.w )
            if data.h < self.record.img_height:
                span_resize.append( A( B( 'S', _style='font-size: 120%;' ),
                                       _href='#',
                                       _onclick=onclick % data,
                                       _title='small size' ) )
                span_resize.append( ' ' )
            data.w = ac.take( CFG_IMG_SIZE_MEDIUM )
            data.h = get_new_heigth( self.record.img_width, self.record.img_height, data.w )
            if data.h < self.record.img_height:
                span_resize.append( A( B( 'M', _style='font-size: 120%;' ),
                                       _href='#',
                                       _onclick=onclick % data,
                                       _title='medium size' ) )
                span_resize.append( ' ' )
            data.w = ac.take( CFG_IMG_SIZE_LARGE )
            data.h = get_new_heigth( self.record.img_width, self.record.img_height, data.w )
            if data.h < self.record.img_height:
                span_resize.append( A( B( 'L', _style='font-size: 120%;' ),
                                       _href='#',
                                       _onclick=onclick % data,
                                       _title='large size' ) )
            span_resize.append( ']' )
            q_sql = (db.attach.org_attach_id == self.record_id)
            children = self.table_model.select( q_sql, orderby='img_width' )
            for c in children:
                c.is_in_disk = attach_factory.is_file_in_static( c.id, db=db )

        img_url = attach_factory.get_url( self.record_id, db=db )
        is_in_disk = attach_factory.is_file_in_static( self.record_id, db=db )
        self.set_result( dict( jscript=script,
                               span_resize=span_resize,
                               img_url=img_url,
                               is_file_in_static=is_in_disk,
                               children=children ) )




