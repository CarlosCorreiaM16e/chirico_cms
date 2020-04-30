# -*- coding: utf-8 -*-

from cgi import FieldStorage

from chirico.app import app_factory
from gluon import current, DIV, H1, IMG, URL, A, SQLFORM, IS_IN_SET, Field
from gluon.storage import Storage
from m16e import term
from m16e.db import attach_factory, db_tables
from m16e.kommon import KQV_OFFSET, KQV_NEXT_C, KQV_NEXT_F, KQV_UPLOAD_FILE, ACT_UPLOAD_FILE, K_ROLE_DEVELOPER, \
    K_ROLE_ADMIN, K_ROLE_MANAGER, K_ROLE_EDITOR, K_ROLE_SUPPORT
from m16e.ktfact import KTF_ACTION
from m16e.ui import elements
from m16e.user_factory import is_in_group
from m16e.views.base_view import BaseView


ACT_DUMP_ALL_FILES = 'act_dump_all_files'


class CmsGridGallery( BaseView ):
    controller_name = 'gallery'
    function_name = 'grid'


    def __init__( self, db ):
        super( CmsGridGallery, self ).__init__( db )
        self.table_model = db_tables.get_table_model( 'attach', db=db )
        self.grid_cols = 6
        self.grid_rows = 3
        self.limit = self.grid_rows * self.grid_cols
        self.offset = 0
        self.col_class = 'col-md-%d' % (12 / self.grid_cols)
        self.url_c = 'gallery'
        self.url_f = 'edit'
        # ac = app_factory.get_app_config_data( db=db )
        # self.isizes = Storage( { db_sets.IMG_SIZE_ORIGINAL: ac[ IMG_SIZE_PAGE ],
        #                          db_sets.IMG_SIZE_MEDIUM: ac[ IMG_SIZE_BLOCK ],
        #                          db_sets.IMG_SIZE_SMALL: ac[ IMG_SIZE_THUMB ] } )
        self.isizes = attach_factory.get_img_sizes( db=db )
        self.form = None
        self.rec_count = None
        self.record_list = []
        self.target = None
        self.nav_prev = ''
        self.nav_next = ''


    def fetch_vars( self ):
        request = current.request
        term.printDebug( 'request.args: ' + repr( request.args ) )
        term.printDebug( 'request.vars: ' + repr( request.vars ) )
        self.action = request.vars.get( KTF_ACTION )
        term.printDebug( 'action: ' + repr( self.action ) )
        self.target = request.args( 0 )
        self.next_c = request.vars.next_c or ''
        self.next_f = request.vars.next_f or ''
        self.next_args = request.vars.next_args or []
        self.offset = int( request.vars.get( KQV_OFFSET, 0 ) )


    def set_form( self ):
        T = current.T
        self.form = SQLFORM.factory( Field( 'qv_page_size', 'integer',
                                            default='P' ) )


    def process_form_action( self ):
        request = current.request
        T = current.T
        db = self.db
        if self.action == ACT_UPLOAD_FILE:
            new_image = request.vars.get( KQV_UPLOAD_FILE )
            filename = request.vars.get( 'qv_filename' )
            short_description = request.vars.get( 'qv_short_description' )
            if new_image is not None and isinstance( new_image, FieldStorage ):
                ut = attach_factory.get_unit_type( meta_name='site_objects', db=db )
                at = attach_factory.get_attach_type( meta_name='images', db=db )
                if not filename:
                    filename = new_image.filename
                new_attach_id = attach_factory.add_attach( attached=new_image,
                                                           attach_type_id=at.id,
                                                           unit_type_id=ut.id,
                                                           filename=filename,
                                                           short_description=short_description,
                                                           is_site_image=True,
                                                           dump_to_static=True,
                                                           db=db )
                sql = '''
                    select count( * )
                    from attach a
                        join attach_type at on at.id = a.attach_type_id
                        join unit_type ut on ut.id = a.unit_type_id
                    where
                        at.meta_name = 'images' and
                        ut.meta_name = 'site_objects' and
                        a.org_attach_id is null and
                        a.filename < '%(f)s' 
                    ''' % dict( f=filename )
                self.rec_count = db.executesql( sql )[ 0 ][ 0 ]
                offset = db.executesql( sql )[ 0 ][ 0 ]
                url_vars = { KQV_OFFSET: offset }
                url_args=[]
                if self.next_c:
                    url_vars[ 'next_c' ] = self.next_c
                    url_vars[ 'next_f' ] = self.next_f
                if self.next_args:
                    url_vars[ 'next_args' ] = self.next_args
                if self.target:
                    url_args = self.target
                return self.set_result( redirect=URL( c=self.controller_name,
                                                      f=self.function_name,
                                                      args=url_args,
                                                      vars=url_vars ),
                                        message=T( 'Image added' ) )


    def process_form( self ):
        request = current.request
        session = current.session
        T = current.T

        #         term.printLog( 'action: ' + repr( self.action ) )
        if self.form.accepts( request.vars, session, dbio=False ):
            self.process_form_action()

        elif self.form.errors:
            term.printLog( 'form.errors: ' + repr( self.form.errors ) )
            term.printLog( 'form.errors: ' + str( self.form.errors ) )
            self.set_result( message=T( 'Form has errors' ) )
        self.errors = self.form.errors


    def process_pre_validation_actions( self ):
        db = self.db
        T = current.T
        if self.action == ACT_DUMP_ALL_FILES:
            ac = app_factory.get_app_config_data( db=db )
            thumb_size = ac[ attach_factory.IMG_SIZE_THUMB ]
            attach_factory.dump_all_files_to_disk( at_meta_name='images',
                                                   ut_meta_name='site_objects',
                                                   thumb_size=thumb_size,
                                                   db=db )
            self.set_result( message=T( 'Files copied to disk' ) )


    def get_record_list( self ):
        db = self.db
        sql = '''
            select count( * )
            from attach a
                join attach_type at on at.id = a.attach_type_id
                join unit_type ut on ut.id = a.unit_type_id
            where
                at.meta_name = 'images' and
                ut.meta_name = 'site_objects' and
                a.org_attach_id is null'''
        self.rec_count = db.executesql( sql )[0][0]
        sql = '''
            select
                a.*,
                at.meta_name
            from attach a
                join attach_type at on at.id = a.attach_type_id
                join unit_type ut on ut.id = a.unit_type_id
            where
                at.meta_name = 'images' and
                ut.meta_name = 'site_objects' and
                a.org_attach_id is null
            order by a.path, a.filename
            offset %(ofs)s limit %(lim)s
        ''' % dict( ofs=self.offset,
                    lim=self.limit )
        term.printDebug( 'sql: %s' % sql )
        ac = app_factory.get_app_config_data( db=db )
        small_size = ac[ attach_factory.IMG_SIZE_THUMB ]
        self.record_list = []
        rows = db.executesql( sql, as_dict=True )
        for row in rows:
            r = Storage( row )
            r.is_file_in_static = attach_factory.is_file_in_static( r.id, db=db )
            child = attach_factory.get_child_by_width( r.id, small_size, db=db )
            if child:
                r.url = attach_factory.get_url( child.id, db=db )
            else:
                r.url = attach_factory.get_url( r.id, db=db )
            r.resize_options = attach_factory.get_resize_options( r, self.isizes, db=db )
            self.record_list.append( r )
        if self.next_c:
            args = [ self.target ]
            vars = Storage( next_c=self.next_c,
                            next_f=self.next_f,
                            next_args=self.next_args )
        else:
            args = []
            vars = Storage()
        if self.offset > 0:
            ofs = self.offset - self.limit
            if ofs < 0:
                ofs = 0
            vars[ KQV_OFFSET ] = ofs
            self.nav_prev = elements.get_link_icon( elements.ICON_CHEVRON_LEFT,
                                                    URL( c=self.controller_name,
                                                         f=self.function_name,
                                                         args=args,
                                                         vars=vars ) )
        ofs = self.offset + self.limit
        if ofs < self.rec_count:
            vars[ KQV_OFFSET ] = ofs
            self.nav_next = elements.get_link_icon( elements.ICON_CHEVRON_RIGHT,
                                                    URL( c=self.controller_name,
                                                         f=self.function_name,
                                                         args=args,
                                                         vars=vars ) )


    def post_process( self ):
        perms = Storage()
        perms.is_dev = is_in_group( K_ROLE_DEVELOPER )
        perms.is_admin = is_in_group( K_ROLE_ADMIN )
        perms.is_manager = is_in_group( K_ROLE_MANAGER )
        perms.is_editor = is_in_group( K_ROLE_EDITOR )
        perms.is_support = is_in_group( K_ROLE_SUPPORT )
        d = dict( form=self.form,
                  errors=self.errors or '',
                  perms=perms,
                  records=self.record_list,
                  rec_count=self.rec_count,
                  rows=self.grid_rows,
                  cols=self.grid_cols,
                  col_class=self.col_class,
                  url_c=self.url_c,
                  url_f=self.url_f,
                  next_c=self.next_c,
                  next_f=self.next_f,
                  next_args=self.next_args,
                  target=self.target,
                  isizes=self.isizes,
                  nav_prev=self.nav_prev,
                  nav_next=self.nav_next )

        self.set_result( d )
        # term.printDebug( 'result.dict: %s' % repr( self.result.dict ) )
        # term.printDebug( 'result.redirect: %s' % ( repr( self.result.redirect ) ) )


    def do_process( self ):
        request = current.request
        session = current.session

        term.printLog( 'request.args: ' + repr( request.args ) )
        term.printLog( 'request.vars.keys: ' + repr( request.vars.keys() ) )
        self.fetch_vars()
        # term.printDebug( 'request.vars: %s' % repr( request.vars ) )
        if self.result.stop_execution and self.result.redirect:
            return self.result

        # term.printLog( 'self.action: ' + repr( self.action ) )

        if self.result.stop_execution and self.result.redirect:
            return self.result

        self.process_pre_validation_actions()
        if self.result.stop_execution and self.result.redirect:
            return self.result

        self.set_form()
        self.process_form()

        self.get_record_list()

        self.post_process()
        # term.printDebug( 'result: %s' % ( repr( self.result ) ) )
        return self.result

