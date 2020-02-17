# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

from m16e.db import db_tables
from gluon.storage import Storage
from m16e import term
from m16e.views.edit_base_view import BaseFormView



class AttachTypeEditView( BaseFormView ):
    def __init__( self, db ):
        super( AttachTypeEditView, self ).__init__( db )
        self.table_model = db_tables.get_table_model( 'attach_type', db=db )


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
#         ACT_SUBMIT_ATTACH_TYPE = 'submit_attach_type'
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
#         attach_type_id = 0
#         attach_type = None
#         if request.args:                    # attach_type
#             attach_type_id = int( request.args( 0 ) )
#             if attach_type_id:
#                 attach_type = db.attach_type[ attach_type_id ]
#
#         term.printLog( 'attach_type_id: ' + repr( attach_type_id ) )
#
#         form = self.get_form( attach_type, deletable=True )
#
#         action = request.post_vars.action
#         term.printLog( 'action: ' + repr( action ) )
#
#         if form.accepts( request.vars, session ):
#             term.printLog( 'next_c: ' + repr( next_c ) )
#             if attach_type:
#                 session.flash = T( 'Attach type updated' )
#             else:
#                 session.flash = T( 'Attach type created' )
#                 if next_c:
#                     d_vars = { 'next_c': next_c,
#                                'next_f': next_f,
#                                'next_args': next_args }
#                     d_vars[ KQR_SELECTED_ID ] = form.vars.id
#                     redirect = URL( c=next_c, f=next_f, args=next_args, vars=d_vars )
#                     return Storage( dict=dict(),
#                                     redirect=redirect )
#
#             redirect = URL( c='attach_type', f='edit', args=[ attach_type_id ] )
#
#         elif form.errors:
#             term.printLog( 'form.errors: ' + repr( form.errors ) )
#             response.flash = T( 'Form has errors' )
#
#         else:
#             response.flash = T( 'Nothing to update' )
#
#         return Storage( dict=dict( attach_type=attach_type, form=form ),
#                         redirect=redirect )
#
#
