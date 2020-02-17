# -*- coding: utf-8 -*-

from gluon import current
from gluon.storage import Storage
from m16e.ktfact import KTF_COLS

LIST_FILTER_POPUP_WINDOW_DIV = 'list_filter_popup_window'
LIST_FILTER_POPUP_BODY_DIV = 'list_filter_popup_body'

class ListFilter( object ):
    '''

    '''
    def __init__( self,
                  plastic_view,
                  db=None ):
        """

        Args:
            plastic_view: BaseListPlasticView
            db:

        self.condition_values: { row_id: row_value }
        self.condition_list: [ <ListFilterCondition> ]
        """
        if not db:
            db = current.db
        self.db = db
        self.plastic_view = plastic_view
        self.condition_values = Storage()
        self.condition_list = []


    def get_field_list( self ):
        fld_list = self.get_query_fields()
        if not fld_list:
            fld_list = self.get_list_fields()
        return fld_list


    def get_list_fields( self ):
        return self.plastic_view.tdef[ KTF_COLS ]


    def get_query_fields( self ):
        return self.plastic_view.qdata[ KTF_COLS ]

