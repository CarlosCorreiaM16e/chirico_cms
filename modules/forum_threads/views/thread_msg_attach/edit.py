# -*- coding: utf-8 -*-

from m16e.db import db_tables
from gluon import current
from m16e.views.edit_base_view import BaseFormView
from gluon.html import A, DIV, SPAN, URL
from m16e.kommon import DATE, DT

#----------------------------------------------------------------------
class RequestMsgAttachEditView( BaseFormView ):
    controller_name = 'request_msg_attachs'

    #----------------------------------------------------------------------
    def __init__( self, db ):
        super( RequestMsgAttachEditView, self ).__init__( db )
        self.table_model = db_tables.get_table_model( 'request_msg_attach', db=db )
#----------------------------------------------------------------------
    def post_process_form( self, form ):
        T = current.T
        super(   RequestMsgAttachEditView, self ).post_process_form( form )
        menu_path = DIV( _id='menu_path_div', _class='menu_path' )
        menu_path.append( A( T( 'RequestMsgAttach' ),
                             _href=URL( c='request_msg_attachs',
                                        f='index' ) ) )
        self.set_result( data=dict( menu_path=menu_path ) )


    #----------------------------------------------------------------------

