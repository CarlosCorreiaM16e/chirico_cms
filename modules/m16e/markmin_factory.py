# -*- coding: utf-8 -*-
import sys
import traceback

from app import db_sets
from chirico.db import lang_factory
from gluon.globals import current
from gluon.html import DIV, URL, IMG, H2, SPAN, A, B, UL, LI, H3, MARKMIN, XML, \
    I, TABLE, TR, TH, TD, CODE, TAG, markmin_serializer
from gluon.storage import Storage
import ast
import m16e.term as term
from m16e.db import db_tables, attach_factory

PERMITTED_TAGS = [
    'a',
    'b',
    'blockquote',
    'br/',
    'i',
    'iframe',
    'li',
    'ol',
    'ul',
    'p',
    'cite',
    'code',
    'pre',
    'img/']

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title' ],
    'img': ['src', 'alt' ],
    'blockquote': ['type'] }

div_css_remove = []

WT_AUTHOR = 'author'
WT_BLOCK = 'block'
WT_CODE = 'code'
WT_EMBED = 'embed'
WT_HEADER = 'header'
WT_IMAGE = 'image'
WT_LINK = 'link'
WT_MEDIA = 'media'
WT_MAIL = 'mailto'
WT_MORE = 'more'
WT_NEWSLIST = 'news_list'
WT_TITLE = 'title'
WT_TIMESTAMP = 'timestamp'

KW_MAX_ARTICLES = 'max_articles'

WIKI_TAGS = {
    WT_AUTHOR: {},
    WT_MORE: {},
    WT_NEWSLIST: { KW_MAX_ARTICLES: 3 },
    WT_TITLE: {},
    WT_TIMESTAMP: {},
}

TAG_PREFIX = '[+['
TAG_SUFFIX = ']+]'
STYLE_SEPARATOR = '+++'
DEFAULT_EMBED_TAG = 'p'
DEFAULT_EMBED_CLASS = 'text-center'


def apply_styles( el, style ):
    if style:
        for k in style:
            if el.attributes.has_key( '_' + k ):
                el[ '_' + k ] = el[ '_' + k ] + ' ' + style[ k ]
            else:
                el[ '_' + k ] = style[ k ]
    return el


def split_with_delimeters( text, start, stop ):
    p1, rest = text.split( start, 1 )
    t, p2 = rest.split( stop, 1 )
    return p1, t, p2


def split_parts( xml_text, tag ): #, handle_styles=True ):
    '''
    text
    [+[mk{}: data]+]
    -> { part1, part2, mk{} }
    '''
    mk_tag = '%s%s' % ( TAG_PREFIX, tag )
    struct = '{}'
    p1, mk_text, p2 = split_with_delimeters( xml_text, mk_tag, TAG_SUFFIX )
    parts = Storage( part1=p1, part2=p2, tag=tag )
    if '{' in mk_text:
        struct, mk_text = mk_text.split( '}' )
        struct += '}'
    # if '}' in mk_text:
    #     struct, mk_text = mk_text.split( '}' )
    #     struct += '}'
    if mk_text[0] == ':':
        mk_text = mk_text[ 1: ]
    term.printDebug( 'struct: %s' % repr( struct ) )

    # parts = xml_text.split( mk_tag, 1 )
    # part1 = parts[0]
    # p2_list = parts[1].split( TAG_SUFFIX, 1 )
    # if len( p2_list ) < 2:
    #     term.printWarn( 'Failed to parse xml_text: %s\nparts: %s\np2_list: %s' %
    #                     (xml_text, repr( parts ), repr( p2_list ) ) )
    #     return None
    # part2 = p2_list[1]
    # parts = Storage( part1=part1, part2=part2, tag=tag )
    # struct, mk_text = {}, p2_list[ 0 ]
    # if '}' in mk_text:
    #     struct, mk_text = mk_text.split( '}' )
    #     struct += '}'
    #     if mk_text[0] == ':':
    #         mk_text = mk_text[ 1: ]
    term.printDebug( 'struct: %s' % repr( struct ) )
    parts.mk = Storage( style=Storage( ast.literal_eval( struct.strip() ) ) )
    parts.mk.text = mk_text

    # if tag[-1] != ' ':
    #     tag += ' '
    #
    # mk_text = tag + p2_list[0]
    #
    # parts = Storage( part1=part1, part2=part2 )
    # s = mk_text.split( ':', 1 )
    # parts.mk = Storage( tag=s[0] )
    # s = s[1].split( STYLE_SEPARATOR, 1 )
    # term.printDebug( 's: %s' % s )
    # if handle_styles:
    #     parts.mk.text = s[0]
    #     if len( s ) > 1:
    #         parts.mk.style = ast.literal_eval( s[1] )
    # else:
    #     parts.mk.style = {}
#     term.printDebug( 'parts: %s' % '\n'.join( [ parts.part1, parts.part2, repr( parts.mk ) ] ) )
    term.printDebug( 'parts: %s' % repr( parts ) )
    return parts


def mk_wt_image( attach_id, align=None, width=None, caption=None, db=None ):
    if not db:
        db = current.db
    a_model = db_tables.get_table_model( 'attach', db=db )
    attach = a_model[ attach_id ]
    if not width:
        width = attach.img_width
    s = '''[+[%(tag)s { 'id': %(id)s, 'link': True, 'width': '%(width)s',''' % dict( tag=WT_IMAGE,
                                                                                     id=attach_id,
                                                                                     width=width )
    if align and align != 'center':
        s += "'align': '%s'," % align
    if caption:
        s += "'caption': '%s'," % caption
    s += ' } '
    # if attach.short_description:
    #     s += ' [%s]' % attach.short_description
    # s += attach_factory.get_url( attach_id, db=db )
    # if align:
    #     s += ' ' + align
    # if width:
    #     s += ' %dpx' % width
    s += ' ]+]'
    return s


def parse_wt_author( block, xml_text, db=None ):
    '''
    [+[author]+]
     -> auth_user.first_name
    '''
    if not db:
        db = current.db
    mk_author = '%s%s%s' % ( TAG_PREFIX, WT_AUTHOR, TAG_SUFFIX )
    au = db.auth_user[ block.created_by ]
    author_sig = '\n%s\n' % (
        DIV( au.first_name,
             _class = 'author_sig' ).xml() )
    txt = xml_text.replace( mk_author, author_sig )
    return txt


def parse_wt_images( xml_text, db=None ):
    '''
    [+[image { 'id': 32, 'filename': 'al-Khwarizm.jpeg',
               'link': True, 'width': '200px', 'caption': '',
               'align': 'center'}]+]
     -> URL( c='survey', f='static', args= [ 'surveys', 59, 'al-Khwarizm.jpeg' ] )
    '''
    if not db:
        db = current.db
    T = current.T
    #     term.printDebug( 'xml_text: %s' % (xml_text ) )
    mk_image = '%s%s ' % (TAG_PREFIX, WT_IMAGE)
    a_model = db_tables.get_table_model( 'attach', db=db )
    bak_xml = xml_text
    try:
        while mk_image in xml_text:
            parts = split_parts( xml_text, WT_IMAGE )
            #         term.printDebug( 'parts: %s' % ( repr( parts ) ) )
            image_id = int( parts.mk.style.id )
            #         term.printDebug( 'image_id: %s' % ( repr( image_id ) ) )
            image = a_model[ image_id ]
            st_filename = attach_factory.is_file_in_static( image_id, db=db )
            #         term.printDebug( 'st_filename: %s' % ( repr( st_filename ) ) )
            if st_filename:
                url = attach_factory.get_url( image_id, db=db )
            else:
                url = URL( c='default', f='download', args=image.attached )
            #         term.printDebug( 'st_filename: %s' % ( repr( st_filename ) ) )
            use_link = bool( parts.mk.style.get( 'link' ) )
            caption = parts.mk.style.get( 'caption' )
            align = parts.mk.style.get( 'align', 'center' )
            width = parts.mk.style.get( 'width' )
            if not width.endswith( 'px' ):
                width += 'px'
            for a in ('link', 'id', 'filename', 'caption', 'align', 'width' ):
                if parts.mk.style.get( a ):
                    del (parts.mk.style[ a ])
            xml = IMG( _src=url )
            xml = apply_styles( xml, parts.mk.style )
            xml[ '_style' ] = 'width: 100%%; object-fit: contain; max-width: %(w)s; margin: auto; display: block;' % dict( w=width )
            if use_link:
                if image.org_attach_id:
                    oi = a_model[ image.org_attach_id ]
                    while oi.org_attach_id:
                        oi = a_model[ oi.org_attach_id ]
                    dest_link = attach_factory.get_url( oi.id, db=db )
                else:
                    dest_link = url
                xml = A( xml, _href=dest_link, _target='blank' )
            if caption:
                if align:
                    css_class = ' class="text-%s"' % align
                else:
                    css_class = ' class="text-center"'
                css_style = 'style="max-width: %(width)s; overflow: hidden; margin: auto;"' % dict( width=width )
                xmlstr = '''
                    <figure %(cls)s %(stl)s>
                        %(x)s
                        <figcaption>%(c)s</figcaption>
                    </figure>
                ''' % dict( cls=css_class,
                            stl=css_style,
                            x=xml.xml(),
                            c=caption )
            else:
                xmlstr = xml.xml()

            #         term.printDebug( 'img: %s' % ( img.xml() ) )
            #         term.printDebug( 'xml: %s' % ( xml.xml() ) )
            xml_text = parts.part1 + xmlstr + parts.part2
    except:
        t, v, tb = sys.exc_info()
        traceback.print_exception( t, v, tb )
        xml_text = '(((' + T( 'FAILED' ) + ': ' + bak_xml + ')))'
    return xml_text


def mk_wt_link( url, text=None, tip=None, css_class=None ):
    lk = "%s%s{ 'url': '%s'" % ( TAG_PREFIX, WT_LINK, url )
    if tip:
        lk += ", 'tip': '%s'" % tip
    if css_class:
        lk += ", 'class': '%s'" % css_class
    lk += '}'
    if text:
        lk += ':' + text
    lk += TAG_SUFFIX
    return lk


def parse_wt_links( xml_text ):
    '''
    [+[link{ 'url': '{{=URL()}}, 'tip': 'some tip', 'class': '', 'target': '_blank', 'new_tab': True }: text ]+]
     -> A( text, _href=url )
    '''
    # term.printDebug( 'sys.path: %s' % sys.path )
#     term.printDebug( 'xml_text: %s' % (xml_text ) )
    T = current.T
    bak_xml = xml_text
    mk_link = '%s%s' % ( TAG_PREFIX, WT_LINK )
    try:
        while mk_link in xml_text:
            parts = split_parts( xml_text, WT_LINK )
            part1 = parts.part1
            part2 = parts.part2
            # <a href="https://archive.org/details/mia2019-grupos">https://archive.org/details/mia2019-grupos</a>
            url = parts.mk.style[ 'url' ]
            # uparts = url.split( 'href="', 1 )
            # uhref = uparts[1].split( '">', 1 )
            a = A( parts.mk.text, _href=url )
            # a = XML( parts.mk.style[ 'url' ] )
            # a.text = parts.mk.text
            tip = parts.mk.style.get( 'tip' )
            if tip:
                a[ '_title' ] = tip
            target = parts.mk.style.get( 'target' )
            if target:
                a[ '_target' ] = target
            new_tab = parts.mk.style.get( 'new_tab' )
            if new_tab and eval( new_tab ):
                a[ '_target' ] = '_blank'
            css_class = parts.mk.style.get( 'class' )
            if css_class:
                a[ '_class' ] = css_class
            xml_text = part1 + a.xml() + part2
    except:
        t, v, tb = sys.exc_info()
        traceback.print_exception( t, v, tb )
        xml_text = '(((' + T( 'FAILED' ) + ': ' + bak_xml + ')))'
    return xml_text


def parse_wt_media( xml_text, db=None ):
    '''
    [+[media 32:audio.mp3+++{ 'link': True, 'width': '200px' }]+]
     -> URL( f='download', args= [ 'audio.mp3' ] )
    '''
    if not db:
        db = current.db
    # term.printDebug( 'sys.path: %s' % sys.path )
#     term.printDebug( 'xml_text: %s' % (xml_text ) )
    mk_media = '%s%s ' % ( TAG_PREFIX, WT_MEDIA )
    while mk_media in xml_text:
        parts = split_parts( xml_text, WT_MEDIA )
#         term.printDebug( 'parts: %s' % ( repr( parts ) ) )
        media_id = int( parts.mk.id )
        del (parts.mk.style[ 'id' ])
#         term.printDebug( 'media_id: %s' % ( repr( media_id ) ) )
        media = db.attach[ media_id ]
        filename = attach_factory.is_file_in_static( media_id, db=db )
        # term.printDebug( 'filename: %s' % (repr( filename )) )
        if filename:
            url = URL( 'static', filename )
        else:
            url = URL( c='default', f='download', args = media.attached )
        # term.printDebug( 'url: %s' % (repr( url )) )
#         term.printDebug( 'st_filename: %s' % ( repr( st_filename ) ) )
        from gluon.contrib.autolinks import expand_one
        xml = XML( expand_one( url, media ) )
        # term.printDebug( 'xml: %s' % xml.xml(), prompt_continue=True )
        use_link = bool( parts.mk.style.get( 'link' ) )
        if use_link:
            del( parts.mk.style[ 'link' ] )

        xml = apply_styles( xml, parts.mk.style )
        # if use_link:
        #     xml = A( xml, _href=url, _target='blank' )

#         term.printDebug( 'img: %s' % ( img.xml() ) )
#         term.printDebug( 'xml: %s' % ( xml.xml() ) )
        xml_text = parts.part1 + xml.xml() + parts.part2

    return xml_text


def mk_wt_embed( embed_text, caption=None, tag=None, css_class=None ):
    if tag is None:
        tag = 'p'
    if css_class is None:
        css_class = 'text-center'
    # data = Storage( prefix=TAG_PREFIX )
    wtdata = ''
    if css_class:
        wtdata += "{\\n  \\'class\\': \\'%s\\'" % css_class
        # data.css_class = css_class
    if tag:
        if css_class:
            wtdata += ', '
        else:
            wtdata += '{ '
        wtdata += "\\n  \\'tag\\': \\'%s\\', " % tag
        # data.tag = tag
    if caption:
        wtdata += "\\n  \\'caption\\': \\'%s\\', " % caption
    if wtdata:
        wtdata += ' }'
    else:
        wtdata = '{}'
    text = TAG_PREFIX + WT_EMBED + wtdata + ':' + '\\n' + \
           embed_text.replace( '\n','' ).replace( '\r','' ) + \
           '\\n' + TAG_SUFFIX
    # wt = ('%(prefix)sembed' + wtdata) % data
    # text = wt + embed_text + TAG_SUFFIX
    term.printDebug( 'text: %s' + text )
    return text


def parse_wt_embed( xml_text ):
    '''
    [+[embed { 'class': 'text-center', 'tag': 'p', 'caption': 'some text' }:
    <iframe>some text display</iframe>
    ]+]
    example:
        >>> parse_wt_code( "[+[embed:text to display]+]" )
    '''
#     term.printDebug( 'xml_text: %s' % (xml_text ) )
    mk_embed = '%s%s' % ( TAG_PREFIX, WT_EMBED )
    bak_xml = xml_text
    T = current.T
    try:
        while mk_embed in xml_text:
            parts = xml_text.split( mk_embed, 1 )
            part1 = parts[ 0 ]
            if part1.endswith( '<p>' ):
                part1 = part1[ : -3 ]
            p2_list = parts[ 1 ].split( TAG_SUFFIX, 1 )
            if len( p2_list ) < 2:
                term.printWarn( 'Failed to parse xml_text: %s\nparts: %s\np2_list: %s' %
                                (xml_text, repr( parts ), repr( p2_list )) )
                return None
            p = p2_list[ 0 ].strip()
            part2 = p2_list[ 1 ]
            if part2.startswith( '</p>' ):
                part2 = part2[ 4 : ]
            styles_str, embed_text = p.split( '}:', 1 )
            styles_str += '}'
            style = ast.literal_eval( styles_str )
            embed_text = embed_text.replace( '&lt;', '<' ).replace( '&gt;', '>' )
            # get width
            w1 = embed_text.split( 'width="', 1 )[1]
            w = float( w1.split( '"', 1 )[0] )
            # get height
            h1 = embed_text.split( 'height="', 1 )[1]
            h = float( h1.split( '"', 1 )[0] )
            r = h / w * 100
            css_class = style.get( 'class', DEFAULT_EMBED_CLASS )
            outer_div = DIV( _class=css_class, _style=' max-width: 640px; margin: auto' )
            css_class = 'video_container'
            css_style = 'position: relative; padding-bottom: %.2f%%; height: 0; overflow: hidden;' % r
            vcontainer = DIV( _class=css_class, _style=css_style )
            vcontainer.append( XML( embed_text ) )
            outer_div.append( vcontainer )
            if 'caption' in style:
                caption = style.get( 'caption' )
                outer_div.append( DIV( caption, _class='video_caption' ) )
            #     if 'tag' in style:
        #         tag = style.get( 'tag' )
        #         del( style[ 'tag' ] )
        #     else:
        #         tag = DEFAULT_EMBED_TAG
        #     css_class = style.get( 'class', DEFAULT_EMBED_CLASS )
        #     css_style = 'style="max-width: %(width)s; overflow: hidden; margin: auto;"' % dict( width=640 )
        #     attr = ' class="%s" %s' % (css_class, css_style)
        #     if 'caption' in style:
        #         caption = style.get( 'caption' )
        #         del( style[ 'caption' ] )
        #         xml = '''
        #             <figure%(attr)s>
        #                 <div style="width: 100%%; object-fit: contain;">
        #                     %(e)s
        #                 </div>
        #                 <figcaption>%(caption)s</figcaption>
        #             </figure>
        #             ''' % dict( tag=tag,
        #                         attr=attr,
        #                         e=embed_text,
        #                         caption=caption )
        #     else:
        #         xml = '''
        # <%(tag)s%(attr)s>
        #     %(e)s
        # </%(tag)s>
        #     ''' % dict( tag=tag,
        #                 attr=attr,
        #                 e=embed_text )
        #     xml = xml.replace( '&lt;', '<' )
        #     xml = xml.replace( '&gt;', '>' )
            xml = outer_div.xml()
            xml_text = part1 + xml + part2
    #     term.printDebug( 'part1: %s' % (part1 if len( part1 ) < 4 else part1[ -4: ]) )
    #     term.printDebug( 'xml: %s' % str( xml ) )
    #     term.printDebug( 'part2: %s' % (part2 if len( part2 ) < 4 else part2[ : 4 ]) )
    except:
        t, v, tb = sys.exc_info()
        traceback.print_exception( t, v, tb )
        xml_text = '(((' + T( 'FAILED' ) + ': ' + bak_xml + ')))'
    # term.printDebug( 'xml_text: %s' % str( xml_text ) )
    return xml_text


#
#     '''
#     [+[image 2:img name+++{ 'link': True, 'width': '20px' }]+] -> URL( c='default', f='download', args = [ {2} ] )
#     '''
#
#     a_model = db_tables.get_table_model( 'attach', db=db )
# #    term.printLog( 'xml_text: %s' % (xml_text ) )
#     mk_image = '%s%s ' % ( TAG_PREFIX, WT_IMAGE )
#     while mk_image in xml_text:
#         parts = split_parts( xml_text, WT_IMAGE )
# #         term.printDebug( 'parts: %s' % ( repr( parts ) ) )
#         image_id = int( parts.mk.tag.split( ' ', 1 )[1].strip() )
#         image = a_model[ image_id ]
#         url = URL( c='default', f='download', args = image.attached )
#         img = IMG( _src=url )
#         xml = img
#         if 'link' in parts.mk.style:
#             link = URL( c='gallery', f='download', args = image.attached )
#             xml = A( img, _href=link, _target='blank' )
#             del( parts.mk.style[ 'link' ] )
#
# #         term.printDebug( 'img: %s' % ( img.xml() ) )
#         xml = apply_styles( img, parts.mk.style )
# #         term.printDebug( 'xml: %s' % ( xml.xml() ) )
#         xml_text = parts.part1 + xml.xml() + parts.part2
#
#     return xml_text


def parse_wt_code( xml_text ):
    '''
    [+[code:text to display+++{ 'class': 'special_one' }]+]
    example:
        >>> parse_wt_code( "Some text [+[code:text to display+++{ 'class': 'special_one' }]+]" )
    '''
#     term.printDebug( 'xml_text: %s' % (xml_text ) )
    mk_code = '%s%s' % ( TAG_PREFIX, WT_CODE )
    while mk_code in xml_text:
        parts = split_parts( xml_text, WT_CODE )
        xml = '<' + parts.mk.tag
        for attr in parts.mk.style:
            xml += ' ' + attr + '="%s"' % parts.mk.style[ attr ]
        xml += '>%s</%s>' % ( parts.mk.text, parts.mk.tag )

#         term.printDebug( 'xml: %s' % ( xml ) )
        xml_text = parts.part1 + '<br><pre>' + xml + '</pre>' + parts.part2

    return xml_text


def parse_wt_mail( xml_text ):
    '''
    [+[mailto:test@example.com?subject=some_subject test@example.com]+]
    '''

#    term.printLog( 'xml_text: %s' % (xml_text ) )
    mkMail = '%s%s:' % ( TAG_PREFIX, WT_MAIL )
    while mkMail in xml_text:
#         term.printLog( 'xml_text: %s' % (xml_text ) )
        # parts = [ '...', 'test@example.com?subject=some_subject (...)]+] (...)' ]
        parts = xml_text.split( mkMail, 1 )
        part1 = parts[0]
        # p2List = [ 'test@example.com?subject=some_subject test@example.com', '...' ]
        p2List = parts[1].split( TAG_SUFFIX, 1 )
        part2 = p2List[1]
        mList = p2List[0].split( ' ', 1 )
        mtText = '<a href="mailto:' + mList[0] + '">' + mList[1] + '</a>'

#         term.printLog( 'p2List: %s' % ( repr( p2List ) ) )
#         term.printLog( 'mtText: %s' % ( repr( mtText ) ) )
        xml_text = part1 + mtText + part2

#     term.printLog( 'xml_text: %s' % ( repr( xml_text ) ) )
    return xml_text


def parse_wt_more( xml_text, article = None, controller = None, function = None ):
    '''
    [+[more]+] -> use article.id
    [+[more 2]+] -> use URL( c = controller, f = function, args = [ 2 ] )
    [+[more:c,f,2,3]+] -> use URL( c = c, f = f, args = [ 2, 3 ] )
    '''
    T = current.T
#    term.printLog( 'xml_text: %s' % ( xml_text ) )
    mkMore = '%s%s' % ( TAG_PREFIX, WT_MORE )
    while mkMore in xml_text:
        parts = xml_text.split( mkMore, 1 )
        part1 = parts[0]
        part2 = parts[1]
        if part2.startswith( TAG_SUFFIX ):
            part2 = part2[ len( TAG_SUFFIX ) : ]
            url = URL( c = controller, f = function, args = [article.id] )

        elif part2[0] == ' ':
            lkarg = part2[1:]
            lkparts = lkarg.split( TAG_SUFFIX, 1 )
            lk = lkparts[0]
            part2 = lkparts[1]
            url = URL( c = controller, f = function, args = [ lk ] )
        elif part2[0] == ':':
            lkarg = part2[1:]
            lkparts = lkarg.split( TAG_SUFFIX, 1 )
            lk = lkparts[0]
            part2 = lkparts[1]
            argparts = lk.split( ',', 1 )
            controller = argparts[0]
            function = argparts[1]
            args = argparts[2:]
            url = URL( c = controller, f = function, args = args )

        else:
            raise Exception( 'Unparsable [+[more]+] at:\n%s' % ( part2 ) )

        a = '<a href="%s">%s <i class="icon-arrow-right"></i></a>' % (
            url, T( 'more' )    )
        xml_text = part1 + a + part2

    return xml_text


def parse_wt_timestamp( xml_text, ts ):
    mk_ts = '%s%s%s' % ( TAG_PREFIX, WT_TIMESTAMP, TAG_SUFFIX )
    span = SPAN( ts.strftime( '%Y-%m-%d' ), _class = 'news_timestamp' )
    xml = xml_text.replace( mk_ts, span.xml()    )
    return xml


def parse_wiki_tags( block, db=None ):
    if not db:
        db = current.db
    blk_text = lang_factory.get_block_body( block=block, db=db )
    if block.body_markup == db_sets.MARKUP_MARKMIN:
        xml_text = MARKMIN( blk_text, autolinks=False, protolinks=False ).xml()
    else:
        xml_text = blk_text
    xml_text = parse_wt_images( xml_text, db=db )
    xml_text = parse_wt_media( xml_text, db=db )
    xml_text = parse_wt_embed( xml_text )
    xml_text = parse_wt_links( xml_text )
    xml_text = parse_wt_code( xml_text )

#    term.printDebug( 'xml_text: %s' % (xml_text ) )
#     xml_text = parse_wt_mail( xml_text )
#    xml_text = parse_wt_more(
#        db, xml_text, article = article,
#        controller = controller, function = function )
#    term.printLog( 'xml_text: %s' % (xml_text ) )
#     if article:
    xml_text = parse_wt_author( block, xml_text, db=db )
# #        term.printDebug( 'xml_text: %s' % (xml_text ) )
#         xml_text = parse_wt_title( xml_text, article.title )
# #        term.printDebug( 'xml_text: %s' % (xml_text ) )
    xml_text = parse_wt_timestamp( xml_text, block.created_on )

#    term.printLog( 'xml_text: %s' % (xml_text ) )
    return xml_text


def from_html( html ):
    if not '<body>' in html:
        html = '<body>%s</body>' % html
    markmin = TAG( html ).element('body').flatten( markmin_serializer )
    return markmin


def get_wiki_help():
    T = current.T
    helpLink = A( T( '(MARKMIN)' ),
                  _href='http://web2py.com/examples/static/markmin.html',
                  _target = 'blank' )
    div = DIV( T( 'Supports WIKI syntax' ) + ' ', helpLink,
               _style='margin-left: 10px;' )
    div.append( I( _class='icon-plus icon-white dark_bg', 
                   _id='toggle_markmin_help_plus',
                   _style='margin-left: 5px;' ) )
    div.append( I( _class='icon-minus icon-white dark_bg', 
                   _id='toggle_markmin_help_minus',
                   _style='margin-left: 5px;' ) )
    
    table = TABLE( _style='width:100%;' )
    table.append( TR( TH( T( 'Code' ), _style='width:50%;' ), 
                      TH( T( 'Result' ), _style='width:50%;' ) ) )
    style = 'font-family: monospace; white-space: pre-wrap;'
    text = '**bold**'
    table.append( TR( TD( text, _style=style, _class='xsmall' ), 
                      TD( MARKMIN( text ), _class='xsmall' ) ) )
    text = "''italic''"
    table.append( TR( TD( text, _style=style, _class='xsmall' ), 
                      TD( MARKMIN( text ), _class='xsmall' ) ) )
    text = "``mono``"
    table.append( TR( TD( text, _style=style, _class='xsmall' ), 
                      TD( MARKMIN( text ), _class='xsmall' ) ) )
    text = '''[+[code:code block
second line
last line]+]'''
    table.append( TR( TD( text, _style=style, _class='xsmall' ),
                      TD( XML( parse_wt_code( text ) ), _class='xsmall' ) ) )
    text = '''[+[embed:html block
    second line
    last line]+]'''
    table.append( TR( TD( text, _style=style, _class='xsmall' ),
                      TD( parse_wt_embed( text ), _class='xsmall' ) ) )
    div.append( DIV( table, _id='toggle_markmin_help_div' ) )
    return div


def get_markmin_extras():
    extra = {
        'code_cpp':lambda text: CODE(text,language='cpp').xml(),
        'code_java':lambda text: CODE(text,language='java').xml(),
        'code_python':lambda text: CODE(text,language='python').xml(),
        'code_html':lambda text: CODE(text,language='html').xml() }
    return extra
