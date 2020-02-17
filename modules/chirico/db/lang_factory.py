# -*- coding: utf-8 -*-

from gluon import current
from m16e.db import db_tables

LANG_PT = 'pt-pt'
LANG_EN = 'en-gb'
ACCEPTED_LANGUAGES = [ LANG_PT, LANG_EN ]

def get_page_aside_title( page_id=None, page=None, db=None ):
    if not db:
        db = current.db
    if not page:
        p_model = db_tables.get_table_model( 'page', db=db )
        page = p_model[ page_id ]
    session = current.session
    lang = session.lang or 'pt-pt'
    if lang == LANG_EN:
        aside_title = page.aside_title_en or '(empty)'
    else:
        aside_title = page.aside_title
    return aside_title


def get_block_body( block_id=None, block=None, db=None ):
    if not db:
        db = current.db
    if not block:
        b_model = db_tables.get_table_model( 'block', db=db )
        block = b_model[ block_id ]
    session = current.session
    lang = session.lang or 'pt-pt'
    if lang == LANG_EN:
        aside_title = block.body_en or '(empty)'
    else:
        aside_title = block.body
    return aside_title


