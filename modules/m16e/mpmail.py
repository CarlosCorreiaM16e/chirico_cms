# -*- coding: utf-8 -*-

import time

import m16e.term as term
from m16e.db import db_tables
from gluon import current, URL
from gluon.storage import Storage
from gluon.tools import Mail
from gluon.utils import web2py_uuid
from m16e.decorators import deprecated
from m16e.kommon import is_sequence


# FORCE_BCC = 'pedidos@memoriapersistente.pt'
DEFAULT_BCC = 'dev@m16e.com'

#----------------------------------------------------------------------
class MpMailException( Exception ):


    def __init__( self, message, error, result, *args, **kwargs ):
        self.message = message
        self.error = error
        self.result = result
        super( MpMailException, self ).__init__( message, error, result, *args, **kwargs )


#------------------------------------------------------------------
def queue_mail( to_list,
                cc=[],
                bcc=[],
                subject='',
                text_body='',
                html_body = '',
                attach_files = [],
                test_only=False,
                db=None ):
    if not db:
        db = current.db
    auth = current.auth
    if not to_list:
        raise Exception( 'To list empty' )

    term.printDebug( '\nto_list: %s\n  cc: %s\n  bcc: %s\nsubject: %s\ntext_body: %s' %
                     ( repr( to_list ), cc, bcc, subject, text_body ) )
    # term.printDebug( '\ntext_body: %s' %
    #                  ( text_body ) )
    mq_model = db_tables.get_table_model( 'mail_queue', db=db )
    mr_model = db_tables.get_table_model( 'mail_recipient', db=db )
    mq_id = mq_model.insert( dict( subject=subject,
                                   text_body=text_body,
                                   auth_user_id=auth.user.id,
                                   mail_cc=', '.join( cc ),
                                   mail_bcc=', '.join( bcc ) ) )
    if is_sequence( to_list ):
        for to in to_list:
            term.printDebug( 'to: %s' % ( repr( to ) ) )
            mr_model.insert( dict( mail_queue_id=mq_id,
                                   email=to ) )
    else:
        mr_model.insert( dict( mail_queue_id=mq_id,
                               email=to_list ) )


#------------------------------------------------------------------
@deprecated( 'use send_mail()')
def sendMail(
    mail, to, cc = [], bcc = [],
    subject = '',
    plainTextBody = '',
    htmlBody = '',
    attachFiles = [],
    test_only=False ):

#     test_only = True
    if bcc:
        if not mail.settings.sender in bcc:
            if isinstance( bcc, list ):
                bcc.append( mail.settings.sender )
            else:
                bcc = [ bcc, mail.settings.sender ]
    else:
        bcc = [ mail.settings.sender ]
    message = plainTextBody
    if plainTextBody and htmlBody:
        message = (plainTextBody, htmlBody)
    elif htmlBody:
        message = htmlBody

    # attchList = []
    # for a in attachFiles:
    #     term.printLog( a )
    #     attchList.append( Mail.Attachment( a ) )
    #
    do_send_mail( to,
                  cc,
                  bcc,
                  subject,
                  message,
                  attachFiles,
                  test_only )

#------------------------------------------------------------------
def send_mail( to,
               cc=[],
               bcc=[],
               subject='',
               plain_text_body='',
               html_body = '',
               attach_files = [],
               test_only=False ):
    mail = current.mail

    message = plain_text_body
    if plain_text_body and html_body:
        message = (plain_text_body, html_body)
    elif html_body:
        message = html_body

    # attch_list = []
    # for a in attach_files:
    #     term.printLog( a )
    #     attch_list.append( Mail.Attachment( a ) )

    if not cc:
        cc = []
    if bcc:
        if not mail.settings.sender in bcc:
            if isinstance( bcc, list ):
                bcc.append( mail.settings.sender )
            else:
                bcc = [ bcc, mail.settings.sender ]
    else:
        bcc = [ mail.settings.sender ]
    do_send_mail( to, cc, bcc, subject, message, attach_files=attach_files, test_only=test_only )


def do_send_mail( to,
                  cc=None,
                  bcc=None,
                  subject='',
                  message='',
                  attach_files=None,
                  test_only=False,
                  force_send=False ):
    mail = current.mail
    if not cc:
        cc = []
    if not bcc:
        bcc = []
    if not isinstance( bcc, (list, tuple) ):
        bcc = [ bcc ]

    if DEFAULT_BCC and not DEFAULT_BCC in bcc:
        bcc.append( DEFAULT_BCC )
    attach_list = []
    if attach_files:
        for a in attach_files:
            # term.printLog( a )
            attach_list.append( Mail.Attachment( a ) )

    term.printLog( 'to: %s\nsubject: %s' % (to, subject) )
    # test_only = True
    from m16e.system import env
    if env.is_dev_server():
        test_only = True
    term.printLog( 'test_only: %s\ncurrent.is_testing: %s' % (repr( test_only ), repr( current.is_testing )) )
    if not force_send and ( test_only or current.is_testing ):
        print( '>>>>> TEST:' )
        print( 'TO: %s' % ( repr( to ) ) )
        print( 'CC: %s' % ( repr( cc ) ) )
        print( 'BCC: %s' % ( repr( bcc ) ) )
        print( 'SUBJECT: %s' % ( str( subject ) ) )
        print( 'BODY: %s' % ( str( message ) ) )
        print( 'ATTACHES: %s' % ( repr( attach_files ) ) )
    else:
        print('>>>>> MAIL:')
        print( 'TO: %s' % ( repr( to ) ) )
        print( 'CC: %s' % ( repr( cc ) ) )
        print( 'BCC: %s' % ( repr( bcc ) ) )
        print( 'SUBJECT: %s' % ( str( subject ) ) )
        res = mail.send( to=to,
                         cc=cc,
                         bcc=bcc,
                         subject=subject,
                         message=message,
                         attachments=attach_list )
        if not res:
            term.printError( '[ERROR]: %s' % type( mail.error ) )
            term.printError( '[ERROR] #: %s' % repr( mail.error[0] ) )
            if len( mail.error > 1 ):
                term.printError( '[ERROR] #: %s' % str( mail.error ) )
            raise MpMailException( 'Mail error: %s\nresult: %s' %
                                        (repr( mail.error ),
                                        repr( res )),
                                   mail.error,
                                   str( res ) )
        else:
            print( 'res: %s' % repr( res ) )


def email_reset_password( auth_user_id,
                          subject=None,
                          message=None,
                          application=None,
                          welcome_app_name=None,
                          db=None ):
    if not db:
        db = current.db
    request = current.request
    sql = '''
        select * 
            from auth_user
            where id = %(uid)s
    ''' % { 'uid': auth_user_id }
    user = Storage( db.executesql( sql, as_dict=True )[0] )
    # user = db.auth_user[ auth_user_id ]
    if not subject:
        subject = 'Bem vindo a %s' % (welcome_app_name if welcome_app_name else request.application.capitalize())
    if not message:
        message = 'Clique na ligação http://%(h)s%(u)s para definir a sua senha.'
    reset_password_key = str( int( time.time() ) ) + '-' + web2py_uuid()
    # user.update_record( reset_password_key=reset_password_key )
    sql = '''
        update auth_user
            set reset_password_key = '%(pk)s'
            where id = %(uid)s
    ''' % { 'pk': reset_password_key,
            'uid': auth_user_id }
    db.executesql( sql )
    url = URL( a=application,
               c='default',
               f='user',
               args=[ 'reset_password' ],
               vars={ 'key': reset_password_key } )
    d = { 'h': current.hostname,
          'u': url }
    do_send_mail( user.email,
                  subject=subject,
                  message=message % d )

