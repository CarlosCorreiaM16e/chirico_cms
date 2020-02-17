# # -*- coding: utf-8 -*-
# from gluon import current
# from gluon.storage import Storage
# from m16e import mpmail
# from m16e.db import db_tables
#
#
# def add_comment( thread_id,
#                  msg_text,
#                  markup,
#                  auth_user_id,
#                  parent_thread_msg_id=None,
#                  db=None ):
#     if not db:
#         db = current.db
#     tm_model = db_tables.get_table_model( 'thread_msg', db=db )
#     data = Storage( thread_id=thread_id,
#                     auth_user_id=auth_user_id,
#                     msg_text=msg_text,
#                     markup=markup )
#     if parent_thread_msg_id:
#         data.parent_thread_msg_id=parent_thread_msg_id
#
#     tm_model.insert( data )
#     mpmail.queue_mail( )
