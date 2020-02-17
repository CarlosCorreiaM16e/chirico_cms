# -*- coding: utf-8 -*-

from forum_threads.db.models.thread import ThreadModel
from forum_threads.db.models.thread_msg import ThreadMsgModel
from forum_threads.db.models.thread_msg_attach import ThreadMsgAttachModel
from forum_threads.db.models.thread_status import ThreadStatusModel
from forum_threads.db.models.thread_subscriber import ThreadSubscribersModel
from forum_threads.db.models.thread_type import ThreadTypeModel
from forum_threads.db.models.thread_visibility import ThreadVisibilityModel
from forum_threads.db.models.thread_vote import ThreadVoteModel

TABLE_LIST = [ ThreadModel,
               ThreadMsgAttachModel,
               ThreadMsgModel,
               ThreadStatusModel,
               ThreadSubscribersModel,
               ThreadTypeModel,
               ThreadVisibilityModel,
               ThreadVoteModel,
               ]
