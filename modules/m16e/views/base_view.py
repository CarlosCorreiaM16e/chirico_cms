# -*- coding: utf-8 -*-
import sys
import traceback

from m16e.db import db_tables
from gluon.dal import DAL
from gluon.globals import current
from gluon.html import SCRIPT, UL, LI, DIV
from gluon.storage import Storage
from m16e import term
from m16e.kommon import KQK_PREFIX, KQV_PREFIX, DT, ACT_SUBMIT, MSG_TYPE_RESPONSE, MSG_TYPE_FLASH
from m16e.user_factory import get_user_message_board


def get_var_from_dict( d, var_name ):
    found = False
    value = None
    if var_name in d:
        found = True
        value = d[ var_name ]
    return (found, value)


def split_chk_var( var_name ):
    parts = var_name.split( '_' )
    prefix = '_'.join( parts[:-1] ) + '_'
    value = int( parts[-1] )
    return prefix, value


class BaseView( object ):
    controller_name = None
    function_name = None


    def __init__( self, db ):
        T = current.T
        if not isinstance( db, DAL ):
            raise Exception( 'Bad instance: %s' % (repr( db ) ) )
        self.db = db
        self.table_model = None
        self.aux_table_models = []

        self.submit_action = ACT_SUBMIT
        self.msg_submit = T( 'Submit' )

        self.constant_values = {}
        self.print_query = False

        self.errors = {}
        self.action = None

        self.result = Storage( dict=Storage( user_message_board=self.get_user_messages() ),
                               redirect=None,
                               ajax_str=None,
                               direct_content=None,
                               direct_content_mime_type=None )
        self.response_message = Storage( msg_type=MSG_TYPE_RESPONSE[1],
                                         msg=None )

        self.next_c = None
        self.next_f = None
        self.next_args = None
        self.next_vars = None

#         term.printDebug( 'result.dict.user_message_board:\n%s' %
#                          ( self.result.dict.user_message_board.xml() ) )


    def get_user_messages( self ):
        T = current.T
        auth = current.auth
        db = self.db
        user_message_board = DIV()
        if auth and auth.user:
            user_message_board = get_user_message_board()
        return user_message_board


    def set_user_message_board( self ):
        db = self.db
        auth = current.auth
        um_model = db_tables.get_table_model( 'user_message', db=db )
        q_sql = (db.user_message.auth_user_id == auth.user.id)
        q_sql &= (db.user_message.display_from == DT.now())
        q_sql &= (db.user_message.ack_when == None)
        um_list = um_model.select( q_sql, orderby='display_from, id')
        ul = UL()
        for um in um_list:
            li = LI( um.msg_text )
        div = DIV( ul )
        self.result.dict.user_message_board = div


    def get_table_name( self ):
        if self.table_model:
            return self.table_model.table_name
        return None


    def get_db_table( self ):
        db = self.db
        if self.table_model:
            db_table = db[ self.table_model.table_name ]
            return db_table
        else:
            table_name = self.get_table_name()
            if table_name:
                return db[ table_name ]
        return None


    def get_db_aux_tables( self ):
        db = self.db
        db_aux_tables = [ db[ t.table_name ] for t in self.aux_table_models ]
        return db_aux_tables


    def set_response_message( self, message, msg_type=None ):
        self.response_message.msg = message
        if msg_type:
            self.response_message.msg_type = msg_type


    def set_result( self,
                    data=None,
                    redirect=None,
                    message=None,
                    append_message=True,
                    stop_execution=None,
                    ajax_str=None,
                    direct_content=None,
                    direct_content_mime_type=None,
                    force_redirect=False ):
        if redirect is not None:
            if self.result.redirect and not force_redirect:
                raise Exception( 'Redirect collision:\n  self: %s\n  new: %s'
                                 % (repr( self.result.redirect ),
                                    repr( redirect )) )
            self.result.redirect = redirect
        if stop_execution is not None:
            self.result.stop_execution = stop_execution
#         term.printDebug( 'message: %s' % repr( message ) )
        if message:
            if append_message and self.response_message.msg:
                self.response_message.msg += message + '. '
            else:
                self.response_message.msg = message + '. '
            if self.result.redirect:
                self.response_message.msg_type = MSG_TYPE_FLASH[1]
#                 term.printDebug( 'message (flash): %s' % repr( message ) )
#                 session.flash = message
            else:
                self.response_message.msg_type = MSG_TYPE_RESPONSE[1]
#                 term.printDebug( 'message (response): %s' % repr( message ) )
#                 response.flash = message
        if self.result.redirect:
            # term.printDebug( 'result.redirect: %s' % ( repr( self.result.redirect ) ),
            #                  print_trace=True,
            #                  prompt_continue=True )
            self.result.stop_execution = True
            term.printLog( 'redirecting to: %s\nmessage:%s' %
                           ( self.result.redirect,
                             repr( self.response_message.msg ) ) )
            self.response_message.msg_type = 'session'
        else:
            self.response_message.msg_type = 'response'

        if data:
            for k in data:
                self.result.dict[ k ] = data[ k ]
#         term.printDebug( 'result.redirect: %s' % ( repr( self.result.redirect ) ) )
        if ajax_str:
            self.result.ajax_str = ajax_str
        if direct_content:
            self.result.direct_content = direct_content
            self.result.direct_content_mime_type = direct_content_mime_type
        # term.printDebug( 'result: %s' % (repr( self.result )) )
        return self.result


    def get_page_js( self ):
        T = current.T
        if self.errors:
            js = '''
                jQuery( function() {
            '''
            for k in self.errors:
                js += '''
                    jQuery( '%(table_name)s_%(fld)s' ).parent().append(
                        '<div class="error" id="%(fld)s__error">%(msg)s</div>' );
                ''' % dict( table_name=self.get_table_name(),
                            fld=k,
                            msg=T( self.errors[k] ) )
            js += '''
                } );
            '''
        else:
            js = ''
        return js


    def get_constant_name( self, field_name ):
        if field_name.startswith( KQK_PREFIX ):
            cfn = field_name[ len( KQK_PREFIX ) : ]
        elif field_name.startswith( KQV_PREFIX ):
            cfn = field_name[ len( KQV_PREFIX ) : ]
        else:
            cfn = field_name
        return cfn


    def get_constant_values( self ):
        return self.constant_values


    def get_constant_value( self, field_name ):
        cv_dict = self.get_constant_values()
#         found = False
#         value = None
        cfn = self.get_constant_name( field_name )
        (found, value) = get_var_from_dict( cv_dict, cfn )
#         if cfn in cv_dict:
#             found = True
#             value = cv_dict[ cfn ]
        return (found, value)


    def set_constant_value( self, field_name, value ):
        self.constant_values[ self.get_constant_name( field_name ) ] = value


    def update_constant_values( self, upd ):
        for cv in self.get_constant_values():
            (found, value) = self.get_constant_value( cv )
            if found:
                upd[ cv ] = value
        return upd


    def do_process( self ):
        raise Exception( 'Base class!' )


    def process( self ):
        session = current.session
        response = current.response
        try:
            ret = self.do_process()
            # term.printDebug( 'result.redirect: %s' % repr( self.result.redirect ) )
            if self.response_message.msg:
                # term.printDebug( 'self.response_message: %s' % repr( self.response_message ) )
                if self.response_message.msg_type == 'session':
                    session.flash = self.response_message.msg
                else:
                    response.flash = self.response_message.msg
        except:
            t, v, tb = sys.exc_info()
            traceback.print_exception( t, v, tb )
            raise
        return ret


