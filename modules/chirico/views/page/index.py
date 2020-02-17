# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

from m16e.db import db_tables
from gluon import current
from m16e import term
from m16e.kommon import ACT_UNCHECK_ALL, ACT_CHECK_ALL, storagize, KDT_INT, KDT_CHAR, ACT_DELETE_ALL_CHECKED
from m16e.ktfact import K_CHK_ID_PREFIX, KTF_BUTTONS, KTF_NAME, KTF_TITLE, KTF_VALUE, KTF_ONCLICK, KTF_CSS_CLASS, \
    KTF_ID, KTF_COL_ORDER, KTF_SORTABLE_COLS, KTF_CELL_CLASS, KTF_COLS, KTF_TYPE, KTF_CELL_LINK, KTF_LINK_C, KTF_LINK_F, \
    KTF_ARGS_F, KTF_CHECKBOXES, KTF_CHECKBOX_ID
from m16e.views.plastic_view import BaseListPlasticView


class PageIndexView( BaseListPlasticView ):
    controller_name = 'page'
    function_name = 'index'


    def __init__( self, db ):
        super( PageIndexView, self ).__init__( db )
        self.table_model = db_tables.get_table_model( 'page', db=db )


    def do_process( self ):
        return super( PageIndexView, self ).do_process()


    def get_table_view_dict( self ):
        T = current.T
        tdef = { KTF_COL_ORDER: [ 'id', 'name', 'url_c', 'url_f', 'url_args' ],
                 KTF_SORTABLE_COLS: [ 'id', 'name', 'url_c', 'url_f', 'url_args' ],
                 KTF_CELL_CLASS: 'table_border',
                 KTF_COLS: { 'id': { KTF_TITLE: T( 'Page Id' ),
                                     KTF_TYPE: KDT_INT,
                                     KTF_CELL_LINK: { KTF_LINK_C: self.controller_name,
                                                      KTF_LINK_F: 'composer',
                                                      KTF_ARGS_F: [ 'id' ],
                                                      KTF_TITLE: T( 'Edit page' ) },
                                     },
                             'name': { KTF_TITLE: T( 'Name' ),
                                       KTF_TYPE: KDT_CHAR },
                             'url_c': { KTF_TITLE: T( 'Controller' ),
                                        KTF_TYPE: KDT_CHAR },
                             'url_f': { KTF_TITLE: T( 'Function' ),
                                        KTF_TYPE: KDT_CHAR },
                             'url_args': { KTF_TITLE: T( 'Arguments' ),
                                        KTF_TYPE: KDT_CHAR },
                             },
                 KTF_CHECKBOXES: [ { KTF_NAME: K_CHK_ID_PREFIX + '%d',
                                     KTF_CHECKBOX_ID: 'id',
                                     KTF_TITLE: T( 'Select' ) },
                                   ],
                 }
        self.tdef = storagize( tdef )
        term.printDebug( 'tdef: %s' % repr( self.tdef ) )
        return self.tdef


    def get_table_qdata_dict( self, extra_buttons={} ):
        T = current.T
        db = self.db
        jq_check_all = '''
            jQuery( 'input[name^="%s"]' ).attr( 'checked', true ); return false;
            ''' % ( K_CHK_ID_PREFIX )
        jq_uncheck_all = '''
            jQuery( 'input[name^="%s"]' ).attr( 'checked', false ); return false;
            ''' % ( K_CHK_ID_PREFIX )
        qdata = { KTF_BUTTONS: [ { KTF_NAME: 'action',
                                   KTF_TITLE: T( 'Check all' ),
                                   KTF_VALUE: ACT_CHECK_ALL,
                                   KTF_ONCLICK: jq_check_all,
                                   KTF_CSS_CLASS: 'btn btn-info' },
                                 { KTF_NAME: 'action',
                                   KTF_TITLE: T( 'Uncheck all' ),
                                   KTF_VALUE: ACT_UNCHECK_ALL,
                                   KTF_ONCLICK: jq_uncheck_all,
                                   KTF_CSS_CLASS: 'btn btn-info' },
                                 { KTF_NAME: 'action',
                                   KTF_TITLE: T( 'Delete checked' ),
                                   KTF_ID: 'bt_delete_checked',
                                   KTF_VALUE: ACT_DELETE_ALL_CHECKED,
                                   KTF_CSS_CLASS: 'btn btn-warning',
                                   KTF_ONCLICK: "return confirm( '%s' )" % T( 'Are you sure?' ) },
                                 ],
                  KTF_COL_ORDER: [],
                 }
        term.printDebug( 'qdata: %s' % repr( qdata ) )
        self.qdata = storagize( qdata )
        return self.qdata


#     #------------------------------------------------------------------
#     def process( self, is_developer=False ):
#         ACT_CHECK_ALL = 'check_all'
#         ACT_DELETE_ALL_CHECKED = 'delete_all_checked'
#         ACT_NEW_PAGE = 'new_page'
#         ACT_UNCHECK_ALL = 'uncheck_all'
#
#         request = current.request
#         response = current.response
#         session = current.session
#         T = current.T
#         db = self.db
#         auth = session.auth
#         redirect = None
#
#         mainPanel = DIV()
#         mainPanel.append( H3( T( 'Pages' ) ) )
#         pages = db( db.page.is_deleted == False ).select( orderby=db.page.title )
#         table = TABLE()
#         for p in pages:
#             tr = TR()
#             if is_developer:
#                 tr.append( TD( INPUT( _type='checkbox', _name='chk-%d' %(p.id) ) ) )
#             tr.append( TD( A( '%s (%d)' % (p.title, p.id),
#                               _href=URL( r=request, f='edit', args=[ p.id ] ) ) ) )
#
#             table.append( tr )
#         span = SPAN()
#         span.append(
#             BUTTON(
#             T( 'New page' ), _name='action', _type='submit',
#                 _value=ACT_NEW_PAGE, _title=T( 'New Page' ) ) )
#         if is_developer:
#             term.printLog( 'user: ' + auth.user.email )
#             span.append(
#                 BUTTON(
#                     T( 'Check all' ), _name='action', _type='submit',
#                     _value=ACT_CHECK_ALL, _title=T( 'Check all' ),
#                     _onclick='''jQuery( 'input[name^="chk-"]' ).attr( 'checked', true ); return false;''' ) )
#             span.append(
#                 BUTTON(
#                     T( 'Uncheck all' ), _name='action', _type='submit',
#                     _value=ACT_UNCHECK_ALL, _title=T( 'Uncheck all' ),
#                     _onclick='''jQuery( 'input[name^="chk-"]' ).attr( 'checked', false ); return false;''' ) )
#             span.append(
#                 BUTTON(
#                     T( 'Delete all checked' ), _name='action', _type='submit',
#                     _value=ACT_DELETE_ALL_CHECKED, _title=T( 'Delete all checked' ) ) )
#         form = FORM( span )
#         form.append( table )
#         form.append( span )
#         mainPanel.append( form )
#         if form.accepts( request.vars, session ):
#             term.printLog( 'form.vars: ' + repr( form.vars ) )
#             term.printLog( 'request.post_vars: ' + repr( request.post_vars ) )
#             action = request.post_vars.action
#             if action == ACT_NEW_PAGE:
#                 redirect = URL( c='page', f='edit', args=[ 0 ] )
#             if action == ACT_DELETE_ALL_CHECKED:
#                 delCount = 0
#                 page_model = PageModel( db )
#                 for chk in form.vars:
#                     value=form.vars[ chk ]
#                     if value == 'on':
#                         delCount += 1
#                         term.printLog( 'chk: ' + repr(value) )
#                         pageId = int( chk.split( '-' )[1] )
#                         term.printLog( 'deleting page %d' % ( pageId ) )
#                         if is_developer:
#                             page_model.purge( pageId, delete_blocks=True )
#                         else:
#                             page_model.set_deleted( pageId, delete_blocks=True )
#
# #                         pg = Page( db, pageId )
# #                         if is_developer:
# #                             pg.delete_cascade()
# #                         else:
# #                             pg.setDeleted()
#                         term.printLog( 'deleted page %d' % ( pageId ) )
#                 session.flash = str( delCount ) + ' ' + T( 'Pages deleted' )
#                 redirect = URL( c='page', f='index' )
#
#         return Storage( dict=dict( main_panel=mainPanel ), redirect=redirect )

