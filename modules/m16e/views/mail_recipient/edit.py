# -*- coding: utf-8 -*-

from m16e.db import db_tables
from m16e.views.edit_base_view import BaseFormView
from m16e.kommon import DATE, DT

#----------------------------------------------------------------------
class MailRecipientEditView( BaseFormView ):
    controller_name = 'mail_recipient'

    #----------------------------------------------------------------------
    def __init__( self, db ):
        super( MailRecipientEditView, self ).__init__( db )
        self.table_model = db_tables.get_table_model( 'mail_recipient', db=db )
    #----------------------------------------------------------------------

