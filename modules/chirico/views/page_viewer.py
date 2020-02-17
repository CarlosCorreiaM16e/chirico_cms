# -*- coding: utf-8 -*-
import ast

from app import db_sets
from chirico.db import lang_factory
from chirico.k import KQV_PAGE_ID, ACT_DELETE_BLOCK, KQV_BLK_ORDER, KQV_CONTAINER  # , KQV_PAGE_BLOCK_ID
from gluon import current, DIV, XML, H2, A, B, UL, URL, LI, H1, MARKMIN, IMG
from gluon.storage import Storage
from m16e import markmin_factory, term
from m16e.db import db_tables
from m16e.kommon import K_ROLE_EDITOR, K_ROLE_DEVELOPER
from m16e.ktfact import KTF_ACTION
from m16e.ui import elements
from m16e.user_factory import is_in_group


def parse_text( block, db=None ):
    if not db:
        db = current.db
    w_text = markmin_factory.parse_wiki_tags( block, db=db )
    return XML( w_text,
                sanitize=False,
                permitted_tags=markmin_factory.PERMITTED_TAGS,
                allowed_attributes=markmin_factory.ALLOWED_ATTRIBUTES )


# def split_parts( xml_text, tag ):
#     '''
#     '''
#     mk_tag = '%s%s' % ( markmin_factory.TAG_PREFIX, tag )
#     parts = xml_text.split( mk_tag, 1 )
#     part1 = parts[0]
#     p2_list = parts[1].split( markmin_factory.TAG_SUFFIX, 1 )
#     if len( p2_list ) < 2:
#         term.printWarn( 'Failed to parse xml_text: %s\nparts: %s\np2_list: %s' %
#                         (xml_text, repr( parts ), repr( p2_list ) ) )
#         return None
#     part2 = p2_list[1]
#     if tag[-1] != ' ':
#         tag += ' '
#     mk_text = tag + p2_list[0]
#
#     parts = Storage( part1=part1, part2=part2 )
#     s = mk_text.split( ':', 1 )
#     parts.mk = Storage( tag=s[0] )
#     s = s[1].split( markmin_factory.STYLE_SEPARATOR, 1 )
#     parts.mk.text = s[0]
#     if len( s ) > 1:
#         parts.mk.style = ast.literal_eval( s[1] )
#     else:
#         parts.mk.style = {}
# #     term.printDebug( 'parts: %s' % '\n'.join( [ parts.part1, parts.part2, repr( parts.mk ) ] ) )
#     return parts



# def pre_parse_images( xml_text ):
#     '''
#     [+[image 32:al-Khwarizm.jpeg+++{ 'link': True, 'width': '200px' }]+]
#      -> URL( c='survey', f='static', args= [ 'surveys', 59, 'al-Khwarizm.jpeg' ] )
#     '''
#     db = current.db
#
#     # term.printDebug( 'sys.path: %s' % sys.path )
#     # from m16e.db import db_tables
#     a_model = db_tables.get_table_model( 'attach', db=db )
# #     term.printDebug( 'xml_text: %s' % (xml_text ) )
#     mk_image = '%s%s ' % ( markmin_factory.TAG_PREFIX, markmin_factory.WT_IMAGE )
#     while mk_image in xml_text:
#         parts = split_parts( xml_text, markmin_factory.WT_IMAGE )
# #         term.printDebug( 'parts: %s' % ( repr( parts ) ) )
#         image_id = int( parts.mk.tag.split( ' ', 1 )[1].strip() )
# #         term.printDebug( 'image_id: %s' % ( repr( image_id ) ) )
#         image = db.attach[ image_id ]
#         st_filename = attach_factory.is_file_in_static( image_id, db=db )
# #         term.printDebug( 'st_filename: %s' % ( repr( st_filename ) ) )
#         if st_filename:
#             url = attach_factory.get_url( image_id, db=db )
#         else:
#             url = URL( c='default', f='download', args = image.attached )
# #         term.printDebug( 'st_filename: %s' % ( repr( st_filename ) ) )
#         xml = IMG( _src=url )
#         use_link = bool( parts.mk.style.get( 'link' ) )
#         if use_link:
#             del( parts.mk.style[ 'link' ] )
#
#         xml = markmin_factory.apply_styles( xml, parts.mk.style )
#         if use_link:
#             xml = A( xml, _href=url, _target='blank' )
#
# #         term.printDebug( 'img: %s' % ( img.xml() ) )
# #         term.printDebug( 'xml: %s' % ( xml.xml() ) )
#         xml_text = parts.part1 + xml.xml() + parts.part2
#
#     return xml_text
#
#
# def pre_parse_media( xml_text ):
#     '''
#     [+[media 32:audio.mp3+++{ 'link': True, 'width': '200px' }]+]
#      -> URL( f='download', args= [ 'audio.mp3' ] )
#     '''
#     db = current.db
#
#     # term.printDebug( 'sys.path: %s' % sys.path )
# #     term.printDebug( 'xml_text: %s' % (xml_text ) )
#     mk_media = '%s%s ' % ( markmin_factory.TAG_PREFIX, markmin_factory.WT_MEDIA )
#     while mk_media in xml_text:
#         parts = split_parts( xml_text, markmin_factory.WT_MEDIA )
# #         term.printDebug( 'parts: %s' % ( repr( parts ) ) )
#         media_id = int( parts.mk.tag.split( ' ', 1 )[1].strip() )
# #         term.printDebug( 'media_id: %s' % ( repr( media_id ) ) )
#         media = db.attach[ media_id ]
#         filename = attach_factory.is_file_in_static( media_id, db=db )
#         # term.printDebug( 'filename: %s' % (repr( filename )) )
#         if filename:
#             url = URL( 'static', filename )
#         else:
#             url = URL( c='default', f='download', args = media.attached )
#         # term.printDebug( 'url: %s' % (repr( url )) )
# #         term.printDebug( 'st_filename: %s' % ( repr( st_filename ) ) )
#         from gluon.contrib.autolinks import expand_one
#         xml = XML( expand_one( url, media ) )
#         # term.printDebug( 'xml: %s' % xml.xml(), prompt_continue=True )
#         use_link = bool( parts.mk.style.get( 'link' ) )
#         if use_link:
#             del( parts.mk.style[ 'link' ] )
#
#         xml = markmin_factory.apply_styles( xml, parts.mk.style )
#         # if use_link:
#         #     xml = A( xml, _href=url, _target='blank' )
#
# #         term.printDebug( 'img: %s' % ( img.xml() ) )
# #         term.printDebug( 'xml: %s' % ( xml.xml() ) )
#         xml_text = parts.part1 + xml.xml() + parts.part2
#
#     return xml_text


# def pre_parse_embeded( xml_text ):
#     '''
#     [+[media 0:embed+++{ 'width': '200',
#                          'text-align': 'center',
#                          'embed': «
#         <iframe width="560" height="315"
#                 src="https://www.youtube.com/embed/U5_ZNDeYyuU"
#                 frameborder="0"
#                 allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture"
#                 allowfullscreen>
#         </iframe>
#         »
#         }]+]
#     '''
#     db = current.db
#
#     # term.printDebug( 'sys.path: %s' % sys.path )
# #     term.printDebug( 'xml_text: %s' % (xml_text ) )
#     mk_media = '%s%s ' % ( markmin_factory.TAG_PREFIX, markmin_factory.WT_MEDIA )
#     while mk_media in xml_text:
#         parts = split_parts( xml_text, markmin_factory.WT_MEDIA )
#         term.printDebug( 'parts: %s' % ( repr( parts ) ) )
#         media_id = int( parts.mk.tag.split( ' ', 1 )[1].strip() )
#         if media_id != 0:
#             raise Exception( 'Bad syntax (media_id): %s' % xml_text )
#
#         xml = XML( parts.mk.embed )
#         xml = markmin_factory.apply_styles( xml, parts.mk.style )
#         # if use_link:
#         #     xml = A( xml, _href=url, _target='blank' )
#
# #         term.printDebug( 'img: %s' % ( img.xml() ) )
# #         term.printDebug( 'xml: %s' % ( xml.xml() ) )
#         xml_text = parts.part1 + xml.xml() + parts.part2
#
#     return xml_text


def get_page_container( page, container_type, db=None ):
    if not db:
        db = current.db
    # session = current.session
    # pb_model = db_tables.get_table_model( 'page_block', db=db )
    b_model = db_tables.get_table_model( 'block', db=db )
    div = DIV( _class='row block_container' )
    if page.aside_title and container_type == db_sets.BLOCK_CONTAINER_ASIDE:
        div = DIV( _class='row block_container aside_container' )
        div.append( H1( lang_factory.get_page_aside_title( page=page, db=db ),
                        _class='col-md-12 aside_title' ) )
    q_sql = (b_model.db_table.page_id == page.id)
    q_sql &= (b_model.db_table.container == container_type)
    b_list = b_model.select( q_sql, orderby='blk_order' )
    if not b_list:
        return None

    for block in b_list:
        if container_type == db_sets.BLOCK_CONTAINER_ASIDE:
            section_cols = page.aside_panel_cols
        else:
            section_cols = page.main_panel_cols
        col_width = 12 / section_cols * block.colspan
        css_class = 'col-md-%d' % col_width
        if block.css_class:
            css_class += ' ' + block.css_class
        # blk_text = lang_factory.get_block_body( block=block, db=db )
        css_class += ' block_display_body'
        if page.aside_title and container_type == db_sets.BLOCK_CONTAINER_ASIDE:
            css_class += ' aside_block'
        if is_in_group( K_ROLE_EDITOR ):
            css_class += ' editor_highlight'
        # if block.body_markup == db_sets.MARKUP_MARKMIN:
        #     blk_text = parse_text( MARKMIN( blk_text, autolinks=False, protolinks=False ).xml(), db=db )
        # else:
        #     blk_text = parse_text( blk_text, db=db )
        blk_text = parse_text( block, db=db )
        blk_text = XML( blk_text )
        b_div = DIV( blk_text, _class=css_class )
        if block.css_style:
            b_div[ '_style' ] = block.css_style
        if is_in_group( K_ROLE_EDITOR ):
            b_div.append( get_edit_link( block, db=db ) )
            b_div.append( get_add_link( block, 'before', db=db ) )
            b_div.append( get_add_link( block, 'after', db=db ) )
            b_div.append( get_del_link( block, db=db ) )
        div.append( b_div )
    return div



def get_add_link( block, position, db=None ):
    '''

    :param block:
    :param position: 'before' | 'after'
    :param db:
    :return:
    '''
    T = current.T
    if position not in ('before', 'after'):
        raise Exception( 'Wrong position (%s)' % str( position ) )
    blk_order = block.blk_order
    if position == 'after':
        blk_order += 1
    ed_id = 'b_%d' % (block.id)
    ed_link = DIV( _class = 'dropdown align_right div_add_block_' + position )
    ed_inner = DIV( _class = 'align_left' )

    # url = URL( c='block', f='edit', args=[ id ] )
    # ed_inner.append( A( T( 'Edit' ), _href = url ) )
    sp = T( position )
    icon = elements.get_bootstrap_icon( elements.ICON_PLUS,
                                        tip=T( 'Add block (%(position)s)',
                                               dict( position=sp ) ) )
    url = URL( c='block', f='composer', vars={ KQV_PAGE_ID: block.page_id,
                                               KQV_BLK_ORDER: blk_order,
                                               KQV_CONTAINER: block.container } )
    ed_inner.append( A( icon,
                       _href = url,
                       _id = ed_id,
                       _role = 'button' ) )
    ed_link.append( ed_inner )
    return ed_link


def get_del_link( block, db=None ):
    T = current.T
    # ed_id = 'b_%d' % (block.id)
    ed_link = DIV( _class = 'dropdown align_right div_del_block' )
    ed_inner = DIV( _class = 'align_left' )

    # url = URL( c='block', f='edit', args=[ id ] )
    # ed_inner.append( A( T( 'Edit' ), _href = url ) )
    icon = elements.get_bootstrap_icon( elements.ICON_MINUS, tip=T( 'Delete block' ) )
    url = URL( c='block', f='composer', args=[ block.id ], vars={ KTF_ACTION: ACT_DELETE_BLOCK } )
    ed_inner.append( A( icon,
                       _href = url,
                       _role = 'button',
                       _onclick="return confirm( '%(msg)s' );" % dict( msg=T( 'Confirm delete block?' ) ) ) )
    ed_link.append( ed_inner )
    return ed_link


def get_edit_link( block, db=None ):
    if not db:
        db = current.db
    T = current.T
    # ed_id = 'b_%d' % (block.block_id)
    css_class = 'dropdown align_right div_edit_block'
    ed_link = DIV( _class=css_class )
    ed_inner = DIV( _class = 'align_left' )
    url = URL( c='block', f='composer', args=[ block.id ] )
    icon = elements.get_bootstrap_icon( elements.ICON_EDIT, tip=T( 'Edit block' ) )
    ed_inner.append( A( icon,
                        _title=T( 'Compose block' ),
                        _href=url,
                        _class='inplace_menu',
                        _role='button' ) )
    # # url = URL( c='block', f='edit', args=[ block_id ] )
    # # ed_inner.append( A( T( 'Edit' ), _href = url ) )
    # icon = elements.get_bootstrap_icon( elements.ICON_EDIT, tip=T( 'Edit block' ) )
    # ed_inner.append( A( icon,
    #                    _href = '#',
    #                    _id = ed_id,
    #                    _class = 'dropdown-toggle',
    #                    _role = 'button',
    #                    **{ '_data-toggle': 'dropdown' } ) )
    # ul = UL( _id = 'menu', _class = 'dropdown-menu', _role = 'menu',
    #          **{ '_aria-labelledby': ed_id } )
    # url = URL( c='block', f='composer', args=[ page_block.block_id ] )
    # ul.append( LI( A( T( 'Compose block' ),
    #                   _href=url, _class=' inplace_menu' ),
    #                _tabindex=-1 ) )
    # if is_in_group( K_ROLE_DEVELOPER ):
    #     url = URL( c='block', f='edit', args=[ page_block.block_id ] )
    #     ul.append( LI( A( T( 'Edit block' ),
    #                       _href=url, _class=' inplace_menu' ),
    #                   _tabindex=-1 ) )
    #     url = URL( c='page', f='composer', args=[ page_block.page_id ] )
    #     ul.append( LI( A( T( 'Compose page' ),
    #                       _href=url, _class=' inplace_menu' ),
    #                    _tabindex=-1 ) )
    # ed_inner.append( ul )
    ed_link.append( ed_inner )
    return ed_link


def get_page( page_id=None,
              url_c=None,
              url_f=None,
              url_args=None,
              db=None ):
    if not db:
        db = current.db
    p_model = db_tables.get_table_model( 'page', db=db )
    if page_id:
        page = p_model[ page_id ]
    else:
        q_sql = (db.page.url_c == url_c)
        q_sql &= (db.page.url_f == url_f)
        if url_args:
            q_sql &= (db.page.url_args == url_args)
        page = p_model.select( q_sql, print_query=True ).first()

    div = DIV( _class='row' )
    main_panel_cols = page.main_panel_cols
    aside_panel_cols = page.aside_panel_cols
    aside = page.aside_position
    main_container = get_page_container( page, db_sets.BLOCK_CONTAINER_MAIN, db=db )
    aside_container = get_page_container( page, db_sets.BLOCK_CONTAINER_ASIDE, db=db )
    col_width = 12 / page.colspan
    if aside_container and aside == db_sets.PANEL_LEFT:
        col_class = 'col-md-%d' % (col_width * aside_panel_cols)
        div.append( DIV( aside_container, _class=col_class ) )
    col_class = 'col-md-%d' % (col_width * main_panel_cols)
    div.append( DIV( main_container, _class=col_class ) )
    if aside_container and aside == db_sets.PANEL_RIGHT:
        col_class = 'col-md-%d' % (col_width * aside_panel_cols)
        div.append( DIV( aside_container, _class=col_class ) )
    if not aside_container:
        div[ '_class' ] += ' single_container_page'
    return div

