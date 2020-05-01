# -*- coding: utf-8 -*-

from gluon import current, URL, IMG, A, TAG
from m16e.db import db_tables, attach_factory


def mk_html_image( attach_id, align=None, width=None, caption=None, db=None ):
    if not db:
        db = current.db
    a_model = db_tables.get_table_model( 'attach', db=db )
    image = a_model[ attach_id ]
    if not width:
        width = image.img_width
    st_filename = attach_factory.is_file_in_static( attach_id, db=db )
    if st_filename:
        url = attach_factory.get_url( attach_id, db=db )
    else:
        url = URL( c='default', f='download', args=image.attached )
    xml = IMG( _src=url )
    xml[ '_style' ] = 'width: 100%%; object-fit: contain; max-width: %(w)s; margin: auto; display: block;' % \
                      dict( w=width )
    dest_link = None
    if image.org_attach_id:
        oi = a_model[ image.org_attach_id ]
        while oi.org_attach_id:
            oi = a_model[ oi.org_attach_id ]
        dest_link = attach_factory.get_url( oi.id, db=db )
    if dest_link:
        xml = A( xml, _href=dest_link, _target='blank' )
    if caption:
        # TAG.first( TAG.second( 'test' ), _key=3 )
        # <first key =\"3\"><second>test</second></first>
        xml = TAG.figure( xml,
                          TAG.figcaption( caption,
                                          _class="text-center" ),
                          _style='max-width: %(width)s;' % dict( width=width ),
                          _class='image_container' )
    else:
        xml = TAG.figure( xml,
                          _style='max-width: %(width)s;' % dict( width=width ),
                          _class='image_container' )

    return xml

