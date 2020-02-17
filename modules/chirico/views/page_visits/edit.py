# -*- coding: utf-8 -*-

import datetime

from m16e.db import db_tables
from m16e.views.edit_base_view import BaseFormView


DT = datetime.datetime
DATE=datetime.date

#----------------------------------------------------------------------
class PageVisitsEditView( BaseFormView ):
    controller_name = 'page_visits'

    #----------------------------------------------------------------------
    def __init__( self, db ):
        super( PageVisitsEditView, self ).__init__( db )
        self.table_model = db_tables.get_table_model( 'page_visit', db=db )
    #----------------------------------------------------------------------

