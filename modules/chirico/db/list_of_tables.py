# -*- coding: utf-8 -*-

from chirico.db.models.app_config import AppConfigModel
from chirico.db.models.app_theme import AppThemeModel
from chirico.db.models.block import BlockModel
from chirico.db.models.block_attach import BlockAttachModel
from chirico.db.models.block_log import BlockLogModel
from chirico.db.models.comment import CommentModel
from chirico.db.models.page import PageModel
from chirico.db.models.page_counter import PageCounterModel
from chirico.db.models.page_log import PageLogModel
from chirico.db.models.user_data import UserDataModel
from forum_threads.db.models.thread import ThreadModel
from forum_threads.db.models.thread_msg import ThreadMsgModel
from forum_threads.db.models.thread_msg_attach import ThreadMsgAttachModel
from forum_threads.db.models.thread_status import ThreadStatusModel
from forum_threads.db.models.thread_subscriber import ThreadSubscribersModel
from forum_threads.db.models.thread_type import ThreadTypeModel
from forum_threads.db.models.thread_visibility import ThreadVisibilityModel
from forum_threads.db.models.thread_vote import ThreadVoteModel
from m16e.db.models.app_logger import AppLoggerModel
from m16e.db.models.attach import AttachModel
from m16e.db.models.attach_type import AttachTypeModel
from m16e.db.models.long_task import LongTaskModel
from m16e.db.models.mail_queue import MailQueueModel
from m16e.db.models.mail_recipient import MailRecipientModel
from m16e.db.models.mime_type import MimeTypeModel
from m16e.db.models.mime_type_ext import MimeTypeExtModel
from m16e.db.models.shared_run import SharedRunModel
from m16e.db.models.user_message import UserMessageModel

TABLE_LIST = [ AppConfigModel,
               AppLoggerModel,
               AppThemeModel,
               AttachModel,
               AttachTypeModel,
               BlockAttachModel,
               BlockModel,
               BlockLogModel,
               CommentModel,
               LongTaskModel,
               MailQueueModel,
               MailRecipientModel,
               MimeTypeExtModel,
               MimeTypeModel,
               PageModel,
               PageCounterModel,
               PageLogModel,
               SharedRunModel,
               ThreadModel,
               ThreadMsgAttachModel,
               ThreadMsgModel,
               ThreadStatusModel,
               ThreadSubscribersModel,
               ThreadTypeModel,
               ThreadVisibilityModel,
               ThreadVoteModel,
               UserDataModel,
               UserMessageModel,
               ]
