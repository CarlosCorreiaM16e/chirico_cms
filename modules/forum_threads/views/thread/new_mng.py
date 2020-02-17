# -*- coding: utf-8 -*-
from cgi import FieldStorage

from gps import gps_factory
from gps.views.support_request.new import RequestNewView
from m16e import term


class RequestNewMngView( RequestNewView ):
    function_name = 'new'


    def __init__( self, db ):
        super( RequestNewMngView, self ).__init__( db )


    def get_exclude_fields( self ):
        return ('comm_time',
                'request_status_id',
                'closed_time',
                'is_waiting_reply')


    # # ----------------------------------------------------------------------
    # def get_form_validators( self ):
    #     db = self.db
    #     self.form_validators = super( RequestNewMngView, self ).get_form_validators()
    #     br_list = gps_factory.get_blm_request_list( db=db )
    #     br_set = { br.id: br.name for br in br_list }
    #     br_set[ 0 ] = ''
    #     self.form_validators[ 'blm_request' ] = br_set
    #     return self.form_validators


