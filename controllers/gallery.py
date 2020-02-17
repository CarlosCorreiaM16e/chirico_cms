# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
from cgi import FieldStorage

from chirico.k import IMG_SIZE_PAGE, IMG_SIZE_BLOCK, IMG_SIZE_THUMB
from chirico.views.gallery.cms_edit_image import CmsGalleryEditImageView
from chirico.views.gallery.image_grid import CmsGridGallery
from chirico.views.gallery.list_images import get_image_list, get_image_list_comps
from chirico.app import app_factory
from m16e.db import db_tables
from gluon.html import URL
from gluon.storage import Storage
from m16e.db import attach_factory
from m16e.kommon import KQV_LIMIT, KQV_OFFSET, KQV_ORDER, KQV_UPLOAD_FILE, KQV_PAGE_SIZE, KQV_BLOCK_SIZE, \
    KQV_THUMB_SIZE, KQV_NEXT_C, KQV_NEXT_F, KQV_NEXT_ARGS
import m16e.term as term
from m16e.views.gallery.choose_image import GalleryChooseImageView
from m16e.views.gallery.choose_site_image import GalleryChooseSiteImageView
from m16e.views.gallery.list import GalleryListView
from pydal import Field

if 0:
    # from globals import Request, Response, Session
    # from cache import Cache
    # from languages import translator
    # from tools import Auth, Crud, Mail, Service, PluginManager

    # API objects
    request = Request()
    response = Response()
    session = Session()
    cache = Cache(request)
    T = translator(request)

    # Objects commonly defined in application model files
    # (names are conventions only -- not part of API)
    db = DAL()
    auth = Auth(db)
    crud = Crud(db)
    mail = Mail()
    service = Service()
    plugins = PluginManager()
    from gluon.sqlhtml import SQLFORM
    from gluon import IS_IN_SET
    from gluon.http import redirect

#     import gluon.languages.translator as T
#
#     import gluon
#     global auth; auth = gluon.tools.Auth()
#     global cache; cache = gluon.cache.Cache()
#     global crud; crud = gluon.tools.Crud()
#     global db; db = gluon.sql.DAL()
#     global request; request = gluon.globals.Request()
#     global response; response = gluon.globals.Response()
#     global service; service = gluon.tools.Service()
#     global session; session = gluon.globals.Session()



ACT_DELETE_ATTACH = 'delete_attach'
ACT_NEW_ATTACH = 'new_attach'
ACT_SUBMIT_ATTACH = 'submit_attach'

#------------------------------------------------------------------
@auth.requires_membership( K_ROLE_EDITOR )
def index():
    term.printLog( 'request.args: %s\n' % ( repr( request.args ) ) )
    term.printLog( 'request.vars: %s\n' % ( repr( request.vars ) ) )
    redirect( URL( c='gallery', f='list', args=request.args ) )

#------------------------------------------------------------------
@auth.requires_membership( K_ROLE_EDITOR )
def list():
    term.printLog( 'request.args: %s\n' % ( repr( request.args ) ) )
    term.printLog( 'request.vars: %s\n' % ( repr( request.vars ) ) )
    view = GalleryListView( db )
    result = view.process()
    if result.redirect:
        redirect( result.redirect )

    return result.dict


@auth.requires_membership( K_ROLE_EDITOR )
def list_images():
    term.printLog( 'request.args: %s\n' % ( repr( request.args ) ) )
    term.printLog( 'request.vars: %s\n' % ( repr( request.vars.keys() ) ) )
    offset = int( request.vars.get( KQV_OFFSET, 0 ) )
    rows = 2
    cols = 6
    data = get_image_list_comps( offset=offset, limit=rows * cols, db=db )
    data.rows = rows
    data.cols = cols
    data.col_class = 'col-md-%d' % (12 / cols)
    data.next_c = request.vars.get( KQV_NEXT_C )
    data.next_f = request.vars.get( KQV_NEXT_F )
    data.next_args = request.vars.get( KQV_NEXT_ARGS )
    data.target = request.args( 0 )
    data.url_c = 'gallery'
    data.url_f = 'edit'
    ac = app_factory.get_app_config_data( db=db )
    op_page_size = ( ('P', T( 'Page' ) + (' %dpx') % ac[ IMG_SIZE_PAGE ] ),
                     ('B', T( 'Block' ) + (' %dpx') % ac[ IMG_SIZE_BLOCK ]),
                     ('T', T( 'Thumbnail' ) + (' %dpx') % ac[ IMG_SIZE_THUMB ]),
                     )
    op_unit_type = ( ('S', T( 'Site images' )),
                     ('W', T( 'Web shop' ) ) )
    data.form = SQLFORM.factory( Field( 'qv_page_size', 'integer',
                                        requires=IS_IN_SET( op_page_size ),
                                        default='P' ),
                                 Field( 'qv_unit_type', 'integer',
                                        requires=IS_IN_SET( op_unit_type ),
                                        default='S' ),
                                 )
    if data.form.accepts( request.vars, session, dbio=False ):
        new_image = request.vars.get( KQV_UPLOAD_FILE )
        if new_image is not None and isinstance( new_image, FieldStorage ):
            qv_page_size = request.vars.qv_page_size
            if qv_page_size == 'P':
                width = ac[ IMG_SIZE_PAGE ]
            elif qv_page_size == 'B':
                width = ac[ IMG_SIZE_BLOCK ]
            elif qv_page_size == 'T':
                width = ac[ IMG_SIZE_THUMB ]
            else:
                width = None
            at_model = db_tables.get_table_model( 'attach_type', db=db )
            ut_model = db_tables.get_table_model( 'unit_type', db=db )
            qv_unit_type = request.vars.qv_unit_type
            if qv_unit_type == 'S':
                q_sql = (db.unit_type.meta_name == 'site_objects')
                at_meta_name = 'images'
            elif qv_unit_type == 'W':
                q_sql = (db.unit_type.meta_name == 'webshop')
                at_meta_name = 'webshop'
            else:
                raise Exception( 'Unknown unit type: %s' % repr( qv_unit_type ) )
            ut = ut_model.select( q_sql ).first()
            q_sql = (db.attach_type.meta_name == at_meta_name)
            at = at_model.select( q_sql ).first()
            attach_factory.add_attach( attached=new_image,
                                       attach_type_id=at.id,
                                       unit_type_id=ut.id,
                                       filename=new_image.filename,
                                       is_site_image=True,
                                       img_width=width,
                                       dump_to_static=True,
                                       db=db )

            redirect( URL( c='gallery', f='list_images' ) )
    return data

# def list_images():
#     term.printLog( 'request.args: %s\n' % ( repr( request.args ) ) )
#     term.printLog( 'request.vars: %s\n' % ( repr( request.vars ) ) )
#     offset = int( request.vars.get( KQV_OFFSET, 0 ) )
#     content = get_image_list( offset=offset, db=db )
#     return dict( content=content )


#------------------------------------------------------------------
@auth.requires_membership( K_ROLE_EDITOR )
def edit():
    term.printLog( 'request.args: ' + repr( request.args ) )
#     term.printLog( 'request.vars: ' + repr( request.vars ) )

    view = CmsGalleryEditImageView( db )
    result = view.process()
    if result.redirect:
        redirect( result.redirect )

    return result.dict


@auth.requires_membership( K_ROLE_EDITOR )
def choose_image():
    term.printLog( 'request.args: ' + repr( request.args ) )
    term.printLog( 'request.vars.keys(): ' + repr( request.vars.keys() ) )
    view = GalleryChooseImageView( db )
    result = view.process()
    term.printDebug( 'result: %s' % (repr( result ) ) )
    if result.redirect:
        redirect( result.redirect )

    return result.dict


@auth.requires_membership( K_ROLE_EDITOR )
def choose_site_image():
    term.printLog( 'request.args: ' + repr( request.args ) )
    term.printLog( 'request.vars.keys(): ' + repr( request.vars.keys() ) )
    view = GalleryChooseSiteImageView( db )
    result = view.process()
    term.printDebug( 'result: %s' % (repr( result ) ) )
    if result.redirect:
        redirect( result.redirect )

    return result.dict

#------------------------------------------------------------------
@auth.requires_membership( K_ROLE_EDITOR )
def ajaxupdmimetype():
    term.printLog( 'request.vars: %s' % repr( request.vars ) )
    mte_model = db_tables.get_table_model( 'mime_type_ext', db=db )
    key = request.vars.keys()[0]
    val = request.vars[key]
    term.printLog( 'key: %s; val: %s' % (repr( key ), repr( val )) )
    ext = val.split( '.' )[-1]
    term.printLog( 'ext: %s' % (repr( ext ) ) )
    q_sql = (db.mime_type_ext.extension.like( ext ))
    mte = mte_model.select( q_sql ).first()
    term.printLog( 'mte: %s' % (repr( mte ) ) )
    jq = '''
        $( '#attach_mime_type_id' ).val( '%s' );
    ''' % ( str( mte.mime_type_id ) )
    return jq

#------------------------------------------------------------------
@auth.requires_membership( K_ROLE_EDITOR )
def ajax_resize():
    term.printLog( 'request.args: ' + repr( request.args ) )
    term.printLog( 'request.vars: ' + repr( request.vars ) )
    attach_id = int( request.args( 0 ) )
    img_width = int( request.vars.img_width or 0 )
    img_height = int( request.vars.img_height or 0 )
    am_model = db_tables.get_table_model( 'attach', db=db )
    term.printLog( 'copy image #%s ' % repr( attach_id ) )
    new_attach_id = am_model.copy_image( auth.user.id,
                                   attach_id,
                                   new_width=img_width,
                                   new_height=img_height,
                                   insert_dim_in_name=True )
    url = URL( c='gallery', f='edit', args=[ new_attach_id ] )
    jq = '''
        window.location( '%(url)s
    ''' % { 'url': url }
    return jq

#------------------------------------------------------------------
@auth.requires_login()
def add_unit_type():
    ut_model = db_tables.get_table_model( 'unit_type', db=db )

    form = SQLFORM( db.unit_type )
    if form.accepts( request ):
        response.flash = T( 'Unit type added' )
        target = request.args[ 0 ]
        response.js = 'jQuery("#%s_dialog-form" ).dialog("close" );' % target
        #update the options they can select their new category in the
        #main form
        response.js += '''
            jQuery("#%s").append("<option value='%s'>%s</option>");
        ''' % (target, form.vars.id, form.vars.name)
        #and select the one they just added
        response.js += """jQuery("#%s").val("%s");""" % (target, form.vars.id)
        #finally, return a blank form in case for some reason they
        #wanted to add another option
        return form
    elif form.errors:
        # silly user, just send back the form and it'll still be in
        # our dialog box complete with error messages
        return form
    else:
        #hasn't been submitted yet, just give them the fresh blank
        #form
        return form

#------------------------------------------------------------------
@auth.requires_membership( K_ROLE_EDITOR )
def dump_to_disk():
    term.printLog( 'request.args: ' + repr( request.args ) )
    term.printLog( 'request.vars: ' + repr( request.vars ) )

    a_model = db_tables.get_table_model( 'attach', db=db )
    a_list = a_model.select()
    for att in a_list:
        attach_factory.file_dump_to_static( att.id )
    session.flash = T( 'Images dumped to static' )
    redirect( URL( c='gallery', f='index' ) )


@auth.requires_membership( K_ROLE_EDITOR )
def grid():
    term.printLog( 'request.args: %s\n' % ( repr( request.args ) ) )
    term.printLog( 'request.vars: %s\n' % ( repr( request.vars.keys() ) ) )
    view = CmsGridGallery( db )
    result = view.process()
    if result.redirect:
        redirect( result.redirect )

    return result.dict
