# -*- coding: utf-8 -*-
from m16e.db.models.app_logger import AppLoggerModel
from m16e.db.models.attach import AttachModel
from m16e.db.models.attach_type import AttachTypeModel
from m16e.db.models.country import CountryModel
from m16e.db.models.county import CountyModel
from m16e.db.models.county_zip_code import CountyZipCodeModel
from m16e.db.models.currency import CurrencyModel
from m16e.db.models.district import DistrictModel
from m16e.db.models.long_task import LongTaskModel
from m16e.db.models.mail_queue import MailQueueModel
from m16e.db.models.mail_recipient import MailRecipientModel
from m16e.db.models.mime_type import MimeTypeModel
from m16e.db.models.mime_type_ext import MimeTypeExtModel
from m16e.db.models.period import PeriodModel
from m16e.db.models.shared_run import SharedRunModel
from m16e.db.models.unit_type import UnitTypeModel
from m16e.db.models.uom import UomModel
from m16e.db.models.uom_type import UomTypeModel
from m16e.db.models.user_message import UserMessageModel
from m16e.db.models.wday import WdayModel

TABLE_LIST = [ AppLoggerModel,
               AttachModel,
               AttachTypeModel,
               CountryModel,
               CountyModel,
               CountyZipCodeModel,
               CurrencyModel,
               DistrictModel,
               LongTaskModel,
               MailQueueModel,
               MailRecipientModel,
               MimeTypeExtModel,
               MimeTypeModel,
               PeriodModel,
               SharedRunModel,
               UnitTypeModel,
               UomModel,
               UomTypeModel,
               UserMessageModel,
               WdayModel,
               ]
