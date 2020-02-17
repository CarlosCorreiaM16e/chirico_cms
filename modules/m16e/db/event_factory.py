# -*- coding: utf-8 -*-

from gluon import current
from m16e import user_factory
from m16e.kommon import DT


def store_event( origin, description, user_id=None, db=None ):
    if not db:
        db = current.db
    if not user_id:
        user_id = user_factory.get_auth_user_id( include_dummy=True, db=db )
    return db.auth_event.insert( time_stamp=DT.now(),
                                 client_ip=current.remote_ip,
                                 user_id=user_id,
                                 origin=origin,
                                 description=description )
