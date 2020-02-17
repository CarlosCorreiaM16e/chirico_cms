# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

import sys
import traceback

from m16e.db import db_tables
from gluon import current, XML, I, DIV, P, BR, URL, A
from gluon.dal import Field
from gluon.sqlhtml import SQLFORM
from gluon.storage import Storage
from gluon.validators import IS_EMAIL
from m16e import term, mpmail
from m16e.kommon import ACT_SUBMIT, DT
from m16e.system import env
from m16e.ui import elements
from m16e.user_factory import is_in_group
from m16e.views.edit_base_view import BaseFormView
from survey.app import app_factory
from survey.db import global_panel_factory

MAX_ZIP_HELPER_ROWS = 50

ACT_ADD_MAIL = 'act_add_mail'
ACT_RESEND_MAIL = 'act_resend_mail'


class UserInviteFriendsView( BaseFormView ):
    controller_name = 'user'
    function_name = 'invite_friends'


    def __init__( self, db ):
        super( UserInviteFriendsView, self ).__init__( db )
        self.table_model = db_tables.get_table_model( 'user_invitation' )
        self.mail_text = None


    def do_process( self ):
        return super( UserInviteFriendsView, self ).do_process()


    def get_send_to_list_contents( self ):
        session = current.session
        T = current.T
        send_to_list = []
        # icon = I( _class='glyphicon glyphicon-minus glyphicon-white',
        #           _style='padding-right: 0.5em;' )
        I( _class='glyphicon glyphicon-minus glyphicon-white',
                  _style='padding-right: 0.5em;' )
        for s in session.send_to_list:
            icon = elements.get_link_icon( elements.ICON_MINUS,
                                           url=URL( c=self.controller_name,
                                                    f='delete_invitation',
                                                    args=[ s ] ),
                                           html_style='padding-right: 0.5em;',
                                           tip=T( 'remove from list' ) )
            send_to_list.append( icon )
            send_to_list.append( ' ' + s )
            send_to_list.append( BR() )
        return DIV( send_to_list,
                    _id='send_to_list_contents_div' )


    def process_pre_validation_actions( self ):
        super( UserInviteFriendsView, self ).process_pre_validation_actions()
        request = current.request
        session = current.session
        auth = session.auth
        if not session.send_to_list:
            session.send_to_list = []
        ac = app_factory.get_app_config_data()
        self.mail_text = ac.ui_text.replace( '[[U]]', '%s (%s)' % (auth.user.first_name, auth.user.email) )
        url = '%(p)s://%(h)s/%(a)s/default/user/register' % { 'p': current.http_protocol,
                                                              'h': env.get_http_hostname(),
                                                              'a': request.application }
        self.mail_text = self.mail_text.replace( '[[L]]', url )
        term.printDebug( 'mail_text: %s' % str( self.mail_text ) )


    def process_form_action( self, form ):
        db = self.db
        session = current.session
        T = current.T
        term.printDebug( 'form.vars: ' + repr( form.vars ) )
        if self.action == ACT_SUBMIT and session.send_to_list:
            ui_model = db_tables.get_table_model( 'user_invitation', db=db )
            send_to = session.send_to_list
            global_panel = global_panel_factory.get_user_global_panel()
            ac = app_factory.get_app_config_data()
            for to in send_to:
                ui_model.insert( dict( global_panel_id=global_panel.id,
                                       invitation_mail=to,
                                       invitation_ts=DT.now() ) )
            mpmail.queue_mail( send_to,
                               subject=ac.ui_title,
                               text_body=self.mail_text )
            session.send_to_list = []
            self.set_result( message=T( 'Invitations sent' ) )


    def post_process_form( self, form ):
        super( UserInviteFriendsView, self ).post_process_form( form )
        is_dev = is_in_group( 'dev' )
        is_editor = is_in_group( 'editor' )

        send_to_list_contents = self.get_send_to_list_contents()
        term.printDebug( 'send_to_list_contents: %s' % str( send_to_list_contents.xml() ) )
        ac = app_factory.get_app_config_data()
        global_panel = global_panel_factory.get_user_global_panel()
        term.printDebug( 'mail_text: %s' % str( self.mail_text ) )
        self.set_result( data=dict( is_dev=is_dev,
                                    is_editor=is_editor,
                                    ui_text=self.mail_text,
                                    ui_title=ac.ui_title,
                                    global_panel=global_panel,
                                    send_to_list_contents=send_to_list_contents ) )


    def get_form( self,
                  form_fields=None,
                  form_validators=None,
                  deletable=None,
                  textarea_rows=None,
                  readonly_fields=None,
                  exclude_fields=None,
                  upload=None,
                  showid=None,
                  buttons=None,
                  extra_fields=None,
                  form_id=None ):

        form = SQLFORM.factory( Field( 'send_to', 'string', notnull=True ) )
        return form


    # def do_process( self ):
    #     request = current.request
    #     response = current.response
    #     session = current.session
    #     T = current.T
    #     db = self.db
    #     auth = session.auth
    #     redirect = None
    #
    #     term.printLog( 'request.args: ' + repr( request.args ) )
    #     term.printLog( 'request.vars: ' + repr( request.vars ) )
    #
    #     if not session.send_to_list:
    #         session.send_to_list = []
    #
    #     gp_model = db_tables.get_table_model( 'global_panel', db=db )
    #     ui_model = db_tables.get_table_model( 'user_invitation', db=db )
    #     ac = app_factory.get_app_config_data()
    #     mail_text = ac.ui_text.replace( '[[U]]', '%s (%s)' % (auth.user.first_name, auth.user.email) )
    #     url = '%(p)s://%(h)s/%(a)s/default/user/register' % { 'p': current.http_protocol,
    #                                                           'h': env.get_http_hostname(),
    #                                                           'a': request.application }
    #     mail_text = mail_text.replace( '[[L]]', url )
    #     action = request.post_vars.action
    #     if not action and request.vars.action:
    #         action = request.vars.action
    #     term.printLog( 'action: ' + repr( action ) )
    #
    #     term.printDebug( 'auth.user: %s' % repr( auth.user ) )
    #     q_sql = (db.global_panel.auth_user_id == auth.user.id)
    #     global_panel = gp_model.select( q_sql ).first()
    #
    #     # form = SQLFORM.factory( Field( 'mail_address', 'text', notnull=True ) )
    #     # if form.accepts( request.vars, session, dbio = False ):
    #     #     term.printLog( 'form.vars: ' + repr( form.vars ) )
    #     #     if action == ACT_SUBMIT:
    #     #         mail_address = request.form_vars.mail_address
    #     #         msg = global_panel_factory.is_user_invited( mail_address )
    #     #         if msg:
    #     #             response.flash = msg
    #     #         else:
    #     #             msg = global_panel_factory.invite_user( global_panel.id,
    #     #                                                     mail_address )
    #     #             response.flash = msg
    #     form = SQLFORM.factory( Field( 'send_to', 'string', notnull=True ) )
    #     term.printLog( 'form.vars: ' + repr( form.vars ) )
    #     if action == ACT_SUBMIT and session.send_to_list:
    #         send_to = session.send_to_list
    #         for to in send_to:
    #             ui_model.insert( dict( global_panel_id=global_panel.id,
    #                                    invitation_mail=to,
    #                                    invitation_ts=DT.now() ) )
    #         mpmail.queue_mail( send_to,
    #                            subject=ac.ui_title,
    #                            text_body=mail_text )
    #         session.send_to_list = []
    #         response.flash = T( 'Invitations sent' )
    #
    #     term.printDebug( 'global_panel: ' + repr( global_panel ) )
    #
    #     is_dev = is_in_group( 'dev' )
    #     is_editor = is_in_group( 'editor' )
    #
    #     # is_interviewer = is_in_group( 'interviewer' )
    #     # is_panel = is_in_group( 'panel' )
    #     send_to_list_contents = self.get_send_to_list_contents()
    #     term.printDebug( 'send_to_list_contents: %s' % str( send_to_list_contents.xml() ) )
    #
    #     return Storage( dict=dict( form=form,
    #                                is_dev=is_dev,
    #                                is_editor=is_editor,
    #                                ui_text=mail_text,
    #                                ui_title=ac.ui_title,
    #                                global_panel=global_panel,
    #                                send_to_list_contents=send_to_list_contents ),
    #                     redirect=redirect )


    def ajax_add_mail( self ):
        '''
        args=[ send_to ]
        '''
        request = current.request
        response = current.response
        T = current.T
        db = self.db
        session = current.session

        term.printLog( 'request.args: %s\n' % ( repr( request.args ) ) )
        term.printLog( 'request.vars: %s\n' % ( repr( request.vars ) ) )
        try:
            if request.vars.send_to:
                res = IS_EMAIL( error_message=T( 'Invalid mail' ) )( request.vars.send_to )
                if res[1]:
                    js = '''
                        jQuery( '.w2p_flash' ).html( '%(msg)s' ).slideDown().fadeOut( %(f)s );
                    ''' % { 'msg': res[1],
                            'f': response.meta.flash_msg_delay or 5000 }
                elif request.vars.send_to in session.send_to_list:
                    js = '''
                        jQuery( '.w2p_flash' ).html( '%(msg)s' ).slideDown().fadeOut( %(f)s );
                    ''' % { 'msg': T( 'Mail already in list'),
                            'f': response.meta.flash_msg_delay or 5000 }
                else:
                    status, msg = global_panel_factory.is_user_invited( request.vars.send_to )
                    js = ''
                    if status == global_panel_factory.INV_ALREADY_INVITED:
                        d_msg = DIV( _class='error_panel' )
                        ui_model = db_tables.get_table_model( 'user_invitation', db=db )
                        q_sql = (db.user_invitation.invitation_mail == request.vars.send_to)
                        q_sql &= (db.user_invitation.global_panel_id == global_panel_factory.get_user_global_panel())
                        ui = ui_model.select( q_sql, orderby='invitation_ts desc', limit=1 ).first()
                        d_msg.append( P( T( 'You have already invited this friend' ),
                                         BR(),
                                         '(',
                                         T( 'last invitation: %s',
                                            ui.invitation_ts.strftime( '%Y-%m-%d %H:%M' ) ),
                                         ')' ) )
                        d_msg.append( P( T( 'Click on "Resend invitation" if you really want to resend it again' +
                                            ' or press the "Cancel" button to dismiss.' ) ) )
                        js += '''
                            jQuery( '#mail_error_msg' ).html( '%(d_msg)s' );
                            jQuery( '#error_panel' ).removeClass( 'hidden' );
                            jQuery( '.w2p_flash' ).html( '%(msg)s' ).slideDown().fadeOut( %(f)s );
                            jQuery( '#error_panel' ).removeClass( 'hidden' );
                        ''' % { 'msg': msg,
                                'f': response.meta.flash_msg_delay or 3000,
                                'd_msg': d_msg.xml()
                                }
                        # js += '''
                        #     jQuery( '#bt_add_mail' ).val( '%(act)s' );
                        #     jQuery( '#bt_add_mail' ).text( '%(text)s' );
                        #     jQuery( '#bt_add_mail' ).removeClass( 'btn-info' ).addClass( 'btn-warning' );
                        #     jQuery( '.w2p_flash' ).html( '%(msg)s' ).slideDown().fadeOut( %(f)s );
                        #     jQuery( '#bt_add_mail' ).click( function() {
                        #         ajax( '{{=URL( c="user", f="ajax_resend_invitation" ) }}',
                        #               [ 'send_to' ],
                        #               ':eval' );
                        #         return false;
                        #     } );
                        # ''' % { 'act': ACT_RESEND_MAIL,
                        #         'text': T( 'Resend invitation' ),
                        #         'msg': msg,
                        #         'f': response.meta.flash_msg_delay or 3000
                        #         }
                    elif status == global_panel_factory.INV_INVITED_BY_OTHER \
                    or status == global_panel_factory.INV_ALREADY_IN_DB:
                        js += '''
                            jQuery( '.w2p_flash' ).html( '%(msg)s' ).slideDown().fadeOut( %(f)s );
                            jQuery( '#error_panel' ).addClass( 'hidden' );
                        ''' % { 'msg': msg,
                                'f': response.meta.flash_msg_delay or 3000 }
                    else:
                        session.send_to_list.append( request.vars.send_to )
                        send_to_list_contents = self.get_send_to_list_contents().xml()
                        term.printDebug( 'send_to_list_contents: %s' % str( send_to_list_contents ) )
                        js = '''
                            jQuery( '#send_to_list_div' ).html( '%(send_to_list)s' );
                            jQuery( '#no_table_send_to' ).val( '' );
                            jQuery( '#error_panel' ).addClass( 'hidden' );
                        ''' % { 'send_to_list': send_to_list_contents }

                term.printDebug( 'js: %s' % ( js ) )
                return js
        except:
            t, v, tb = sys.exc_info()
            traceback.print_exception( t, v, tb )
        return ''


    def ajax_resend_invitation( self ):
        '''
        args=[ send_to ]
        '''
        request = current.request
        response = current.response
        T = current.T
        db = self.db
        session = current.session

        term.printLog( 'request.args: %s\n' % ( repr( request.args ) ) )
        term.printLog( 'request.vars: %s\n' % ( repr( request.vars ) ) )
        try:
            if request.vars.send_to:
                res = IS_EMAIL( error_message=T( 'Invalid mail' ) )( request.vars.send_to )
                if res[1]:
                    js = '''
                        jQuery( '.w2p_flash' ).html( '%(msg)s' ).slideDown().fadeOut( %(f)s );
                        jQuery( '#error_panel' ).addClass( 'hidden' );
                    ''' % { 'msg': res[1],
                            'f': response.meta.flash_msg_delay or 3000 }
                elif request.vars.send_to in session.send_to_list:
                    js = '''
                        jQuery( '.w2p_flash' ).html( '%(msg)s' ).slideDown().fadeOut( %(f)s );
                        jQuery( '#error_panel' ).addClass( 'hidden' );
                    ''' % { 'msg': T( 'Mail already in list'),
                            'f': response.meta.flash_msg_delay or 3000 }
                else:
                    status, msg = global_panel_factory.is_user_invited( request.vars.send_to )
                    js = ''
                    if status == global_panel_factory.INV_ALREADY_INVITED:
                        session.send_to_list.append( request.vars.send_to )
                        # send_to_list = []
                        # icon = '<i class="glyphicon glyphicon-minus glyphicon-white" style="padding-right: 0.5em;"></i>'
                        # for s in session.send_to_list:
                        #     send_to_list.append( '%s %s<br>' % (s, A( icon,
                        #                                               _href=URL( c=self.controller_name,
                        #                                                          f='delete_invitation',
                        #                                                          args=[ s ] ) ) ) )
                        send_to_list_contents = self.get_send_to_list_contents().xml()
                        term.printDebug( 'send_to_list_contents: %s' % str( send_to_list_contents ) )
                        js += '''
                            jQuery( '#send_to_list_div' ).html( '%(send_to_list)s' );
                            jQuery( '#no_table_send_to' ).val( '' );
                            jQuery( '#bt_add_mail' ).val( '%(act)s' );
                            jQuery( '#bt_add_mail' ).text( '%(text)s' );
                            jQuery( '#error_panel' ).addClass( 'hidden' );
                        ''' % { 'send_to_list': send_to_list_contents,
                                'act': ACT_ADD_MAIL,
                                'text': T( 'Add' )
                                }

                term.printDebug( 'js: %s' % ( js ) )
                return js
        except:
            t, v, tb = sys.exc_info()
            traceback.print_exception( t, v, tb )
        return ''


    def delete_invitation( self ):
        '''
        args=[ send_to ]
        '''
        request = current.request
        response = current.response
        T = current.T
        db = self.db
        session = current.session

        term.printLog( 'request.args: %s\n' % ( repr( request.args ) ) )
        term.printLog( 'request.vars: %s\n' % ( repr( request.vars ) ) )
        try:
            send_to = request.args( 0 )
            if send_to:
                res = IS_EMAIL( error_message=T( 'Invalid mail' ) )( send_to )
                if res[1]:
                    return self.set_result( redirect=URL( c=self.controller_name,
                                                          f=self.function_name ),
                                            message=res[1] )

                elif send_to in session.send_to_list:
                    del session.send_to_list[ session.send_to_list.index( send_to ) ]
                    return self.set_result( redirect=URL( c=self.controller_name,
                                                          f=self.function_name ),
                                            message=T( 'Removed %s', send_to ) )
            return self.result

        except:
            t, v, tb = sys.exc_info()
            traceback.print_exception( t, v, tb )
        return ''



