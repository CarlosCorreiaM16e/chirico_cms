# -*- coding: utf-8 -*-
from gluon import current
from m16e import user_factory
from m16e.db import event_factory


EVT_THREAD_CREATED = 'User %(user)s added thread %(thread_id)s'
EVT_THREAD_DELETED = 'User %(user)s deleted thread %(thread_id)s'
EVT_THREAD_UPDATED = 'User %(user)s updated thread %(thread_id)s'
EVT_COMMENT_CREATED = 'User %(user)s added comment %(comment_id)s'
EVT_COMMENT_DELETED = 'User %(user)s deleted comment %(comment_id)s'
EVT_COMMENT_UPDATED = 'User %(user)s updated comment %(comment_id)s'

def store_thread_created( thread_id, db=None ):
    if not db:
        db = current.db
    T = current.T
    user_id = user_factory.get_auth_user_id( include_dummy=True, db=db )
    return event_factory.store_event( user_factory.EVT_ORIGIN_FORUM,
                                      T( EVT_THREAD_CREATED, dict( user=user_id, thread_id=thread_id ) ),
                                      user_id=user_id, db=db )


def store_thread_updated( thread_id, db=None ):
    if not db:
        db = current.db
    T = current.T
    user_id = user_factory.get_auth_user_id( include_dummy=True, db=db )
    return event_factory.store_event( user_factory.EVT_ORIGIN_FORUM,
                                      T( EVT_THREAD_UPDATED, dict( user=user_id, thread_id=thread_id ) ),
                                      user_id=user_id, db=db )


def store_thread_deleted( thread_id, db=None ):
    if not db:
        db = current.db
    T = current.T
    user_id = user_factory.get_auth_user_id( include_dummy=True, db=db )
    return event_factory.store_event( user_factory.EVT_ORIGIN_FORUM,
                                      T( EVT_THREAD_DELETED, dict( user=user_id, thread_id=thread_id ) ),
                                      user_id=user_id, db=db )


def store_comment_created( comment_id, db=None ):
    if not db:
        db = current.db
    T = current.T
    user_id = user_factory.get_auth_user_id( include_dummy=True, db=db )
    return event_factory.store_event( user_factory.EVT_ORIGIN_FORUM,
                                      T( EVT_COMMENT_CREATED, dict( user=user_id, comment_id=comment_id ) ),
                                      user_id=user_id, db=db )


def store_comment_updated( comment_id, db=None ):
    if not db:
        db = current.db
    T = current.T
    user_id = user_factory.get_auth_user_id( include_dummy=True, db=db )
    return event_factory.store_event( user_factory.EVT_ORIGIN_FORUM,
                                      T( EVT_COMMENT_UPDATED, dict( user=user_id, comment_id=comment_id ) ),
                                      user_id=user_id, db=db )


def store_comment_deleted( comment_id, db=None ):
    if not db:
        db = current.db
    T = current.T
    user_id = user_factory.get_auth_user_id( include_dummy=True, db=db )
    return event_factory.store_event( user_factory.EVT_ORIGIN_FORUM,
                                      T( EVT_COMMENT_DELETED, dict( user=user_id, comment_id=comment_id ) ),
                                      user_id=user_id, db=db )


