# -*- coding: utf-8 -*-

from gluon import current
from m16e import user_factory
from m16e.db import event_factory


EVT_BLOCK_CREATED = 'User %(user)s created block %(block_id)s'
EVT_BLOCK_DELETED = 'User %(user)s deleted block %(block_id)s'
EVT_BLOCK_UPDATED = 'User %(user)s updated block %(block_id)s'
EVT_PAGE_CREATED = 'User %(user)s created page %(page_id)s'
EVT_PAGE_DELETED = 'User %(user)s deleted page %(page_id)s'
EVT_PAGE_UPDATED = 'User %(user)s updated page %(page_id)s'

def store_block_created( block_id, db=None ):
    if not db:
        db = current.db
    user_id = user_factory.get_auth_user_id( include_dummy=True, db=db )
    return event_factory.store_event( user_factory.EVT_ORIGIN_CMS,
                                      EVT_BLOCK_CREATED % dict( user=user_id, block_id=block_id ),
                                      user_id=user_id, db=db )


def store_block_updated( block_id, db=None ):
    if not db:
        db = current.db
    user_id = user_factory.get_auth_user_id( include_dummy=True, db=db )
    return event_factory.store_event( user_factory.EVT_ORIGIN_CMS,
                                      EVT_BLOCK_UPDATED % dict( user=user_id, block_id=block_id ),
                                      user_id=user_id, db=db )


def store_block_deleted( block_id, db=None ):
    if not db:
        db = current.db
    user_id = user_factory.get_auth_user_id( include_dummy=True, db=db )
    return event_factory.store_event( user_factory.EVT_ORIGIN_CMS,
                                      EVT_BLOCK_DELETED % dict( user=user_id, block_id=block_id ),
                                      user_id=user_id, db=db )


def store_page_created( page_id, db=None ):
    if not db:
        db = current.db
    user_id = user_factory.get_auth_user_id( include_dummy=True, db=db )
    return event_factory.store_event( user_factory.EVT_ORIGIN_CMS,
                                      EVT_PAGE_CREATED % dict( user=user_id, page_id=page_id ),
                                      user_id=user_id, db=db )


def store_page_updated( page_id, db=None ):
    if not db:
        db = current.db
    user_id = user_factory.get_auth_user_id( include_dummy=True, db=db )
    return event_factory.store_event( user_factory.EVT_ORIGIN_CMS,
                                      EVT_PAGE_UPDATED % dict( user=user_id, page_id=page_id ),
                                      user_id=user_id, db=db )


def store_page_deleted( page_id, db=None ):
    if not db:
        db = current.db
    user_id = user_factory.get_auth_user_id( include_dummy=True, db=db )
    return event_factory.store_event( user_factory.EVT_ORIGIN_CMS,
                                      EVT_PAGE_DELETED % dict( user=user_id, page_id=page_id ),
                                      user_id=user_id, db=db )


