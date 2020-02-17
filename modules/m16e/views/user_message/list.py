# -*- coding: utf-8 -*-
import sys
import traceback

from gluon.storage import Storage
from m16e.db import db_tables
from gluon import current, SQLFORM, IS_NOT_EMPTY, URL
from m16e import term, mpmail, user_factory
from m16e.db.querydata import QueryData
from m16e.kommon import KQV_SHOW_ALL, KDT_CHAR, KDT_BOOLEAN, KDT_INT, KDT_TIMESTAMP, storagize
from m16e.ktfact import KTF_COL_ORDER, KTF_SORTABLE_COLS, KTF_CELL_CLASS, \
    KTF_COLS, KTF_TITLE, KTF_TYPE, \
    KTF_CELL_LINK, KTF_LINK_C, KTF_LINK_F, KTF_ARGS, KTF_ARGS_F, \
    KTF_BUTTONS
from m16e.views.plastic_view import BaseListPlasticView
from pydal import Field


class UserMsgListView( BaseListPlasticView ):
    controller_name = 'user_message'
    function_name = 'list'


    def __init__( self, db ):
        super( UserMsgListView, self ).__init__( db )

        T = current.T
        self.table_model = db_tables.get_table_model( 'user_message', db=db )

        self.list_title = T( 'User message list' )


    #        term.printDebug( 'query_vars: %s' % repr( self.query_vars ) )

    def get_table_view_dict( self ):
        T = current.T
        tdef = {
            KTF_COL_ORDER: [ 'id', 'first_name', 'msg_title', 'times_viewed',
                             'period_start', 'period_stop', 'ack_when' ],
            KTF_SORTABLE_COLS: [ 'id', 'notify_user_id', 'msg_title', 'times_viewed',
                             'period_start', 'period_stop', 'ack_when' ],
            KTF_CELL_CLASS: 'table_border',
            KTF_COLS: { 'id': { KTF_TITLE: T( 'Id' ),
                                KTF_TYPE: KDT_INT,
                                KTF_CELL_CLASS: 'table_border',
                                KTF_CELL_LINK: { KTF_LINK_C: self.controller_name,
                                                 KTF_LINK_F: 'edit',
                                                 KTF_ARGS_F: [ 'id' ]
                                                 }
                                },
                        'first_name': { KTF_TITLE: T( 'User' ),
                                        KTF_TYPE: KDT_CHAR,
                                        KTF_CELL_CLASS: 'table_border',
                                        },
                        'msg_title': { KTF_TITLE: T( 'Msg title' ),
                                       KTF_TYPE: KDT_CHAR,
                                       KTF_CELL_CLASS: 'table_border',
                                       },
                        'msg_text': { KTF_TITLE: T( 'Msg text' ),
                                      KTF_TYPE: KDT_CHAR,
                                      KTF_CELL_CLASS: 'table_border',
                                      },
                        'times_viewed': { KTF_TITLE: T( 'Times viewed' ),
                                          KTF_TYPE: KDT_INT,
                                          KTF_CELL_CLASS: 'table_border',
                                          },
                        'period_start': { KTF_TITLE: T( 'Period start' ),
                                          KTF_TYPE: KDT_TIMESTAMP,
                                          KTF_CELL_CLASS: 'table_border',
                                          },
                        'period_stop': { KTF_TITLE: T( 'Period stop' ),
                                         KTF_TYPE: KDT_TIMESTAMP,
                                         KTF_CELL_CLASS: 'table_border',
                                         },
                        'ack_when': { KTF_TITLE: T( 'Ack when' ),
                                      KTF_TYPE: KDT_TIMESTAMP,
                                      KTF_CELL_CLASS: 'table_border',
                                      },
                        },
            }
        self.tdef = storagize( tdef )
        return self.tdef


    def get_table_qdata_dict( self, extra_buttons={ } ):
        T = current.T
        qdata = { KTF_BUTTONS: [ ],
                  KTF_COL_ORDER: [],
                  KTF_COLS: { },
                  }
        self.qdata = storagize( qdata )
        return self.qdata


    def get_query_data( self, orderby=None ):
        qd = super( UserMsgListView, self ).get_query_data( orderby )
        term.printDebug( repr( qd ) )
        return qd


    def get_query_select( self ):
        sql = '''
            select um.*, au.first_name
        '''
        return sql


    def get_query_from( self ):
        sql = '''
            from user_message um
                join auth_user au on um.notify_user_id = au.id
        '''
        return sql



    def send_mail( self ):
        request = current.request
        response = current.response
        mail = current.mail
        T = current.T

        term.printLog( 'request.args: %s\n' % ( repr( request.args ) ) )
        term.printLog( 'request.vars: %s\n' % ( repr( request.vars ) ) )

        uidList = request.args
        term.printLog( repr( uidList ) )

        qd = QueryData( 'au.id in ( %(list)s )' % { 'list': ', '.join( uidList ) } )

        user_list = self.get_record_list( qd )
        form = SQLFORM.factory(
            Field( 'mail_subject', 'string', requires = IS_NOT_EMPTY() ),
            Field( 'mail_text', 'text', requires = IS_NOT_EMPTY() ) )
        if form.process().accepted:
            for u in user_list:
                mpmail.send_mail( u.email,
                                  subject=form.vars.mail_subject,
                                  plain_text_body=form.vars.mail_text )
            response.flash = T( 'Mail sent' )
        elif form.errors:
            response.flash = T( 'Errors in form' )
        return Storage( dict=dict( user_list=user_list, form=form ), redirect=None )


    def send_message( self ):
        request = current.request
        response = current.response
        T = current.T
        db = self.db
        term.printLog( 'request.args: %s\n' % (repr( request.args )) )
        term.printLog( 'request.vars: %s\n' % (repr( request.vars )) )
        try:
            uid_list = request.args
            term.printLog( repr( uid_list ) )

            qd = QueryData(
                'au.id in ( %(list)s )' % { 'list': ', '.join( uid_list ) } )

            user_list = self.get_record_list( qd )
            form = SQLFORM.factory(
                # Field( 'erp_blm_id', 'integer', requires=IS_IN_SET( ee_options ) ),
                Field( 'msg_title', 'string', requires=IS_NOT_EMPTY() ),
                Field( 'msg_text', 'text', requires=IS_NOT_EMPTY() ) )
            if form.process().accepted:
                # data = dict( notify_user_id=notify_user_id,
                #              msg_title=msg_title,
                #              msg_text=msg_text,
                #              msg_type=msg_type,
                #              delete_if_past=delete_if_past )
                data = dict( msg_title=form.vars.msg_title,
                             msg_text=form.vars.msg_text,
                             erp_blm_id=form.vars.erp_blm_id )
                for u in user_list:
                    term.printDebug( 'u (%s): %s' % (type( u ), repr( u )) )
                    data[ 'notify_user_id' ] = u.id
                    user_factory.add_user_message( data, db=db )
                self.set_result( message=T( 'Message created' ),
                                 redirect=URL( c=self.controller_name,
                                               f='list' ) )

            elif form.errors:
                response.flash = T( 'Errors in form' )
        except:
            t, v, tb = sys.exc_info()
            traceback.print_exception( t, v, tb )
            raise
        return Storage( dict=dict( user_list=user_list, form=form ), redirect=None )


