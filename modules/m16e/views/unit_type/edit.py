# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

from m16e import term
from m16e.db import db_tables
from m16e.views.edit_base_view import BaseFormView


#------------------------------------------------------------------
class UnitTypeEditView( BaseFormView ):
    controller_name = 'unit_type'
    function_name = 'edit'


    def __init__( self, db ):
        super( UnitTypeEditView, self ).__init__( db )
        self.table_model = db_tables.get_table_model( 'unit_type', db=db )

#     #------------------------------------------------------------------
#     def get_form( self, db_record=None, form_fields=[], form_validators={}, deletable=False ):
#         if not form_fields:
#             form_fields = [ 'name',
#                             'path' ]
#         form = super( UnitTypeEditView, self ).get_form( db_record, form_fields, form_validators, deletable )
#         return form
#
#     #------------------------------------------------------------------
#     def process( self ):
#         #------------------------------------------------------------------
#         request = current.request
#         response = current.response
#         session = current.session
#         T = current.T
#         db = self.db
#         auth = session.auth
#         redirect = None
#
# #         MimeTypeModel( db ).define_table()
#
#         ACT_SUBMIT_UNIT_TYPE = 'submit_unit_type'
#
#         term.printLog( 'request.args: ' + repr( request.args ) )
#         term.printLog( 'request.vars: ' + repr( request.vars ) )
#         if request.post_vars:
#             term.printLog( 'request.post_vars: ' + repr( request.post_vars ) )
#
#         next_c = request.vars.next_c or ''
#         next_f = request.vars.next_f or ''
#         next_args = request.vars.next_args or []
#
#         unit_type_id = 0
#         unit_type = None
#         if request.args:                    # unit_type
#             unit_type_id = int( request.args( 0 ) )
#             if unit_type_id:
#                 unit_type = db.unit_type[ unit_type_id ]
#
#         term.printLog( 'unit_type_id: ' + repr( unit_type_id ) )
#
#         form = self.get_form( unit_type, deletable=True )
#
#         action = request.post_vars.action
#         term.printLog( 'action: ' + repr( action ) )
#
#         if form.accepts( request.vars, session ):
#             if unit_type:
#                 session.flash = T( 'Unit type updated' )
#             else:
#                 session.flash = T( 'Unit type created' )
#                 if next_c:
#                     d_vars = { 'next_c': next_c,
#                                'next_f': next_f,
#                                'next_args': next_args }
#                     d_vars[ KQR_SELECTED_ID ] = form.vars.id
#                     redirect = URL( c=next_c, f=next_f, args=next_args, vars=d_vars )
#
#             redirect = URL( c='unit_type', f='edit', args = [ unit_type_id ] )
#
#         elif form.errors:
#             term.printLog( 'form.errors: ' + repr( form.errors ) )
#             response.flash = T( 'Form has errors' )
#
#         else:
#             response.flash = T( 'Nothing to update' )
#
#         return Storage( dict=dict( unit_type=unit_type, form=form ),
#                         redirect=redirect )
#
#
