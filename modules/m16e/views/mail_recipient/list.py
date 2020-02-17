# -*- coding: utf-8 -*-
import re

from m16e.db import db_tables
from gluon import current, A, URL
from m16e import term
from m16e.db.querydata import QueryData
from m16e.kommon import KQV_SHOW_ALL, KQV_PREFIX, KDT_CHAR, KDT_BLOB_IMG, \
    KDT_BOOLEAN, KDT_INT, KDT_DATE, KDT_DEC, KDT_FILE, KDT_TIME, KDT_TIMESTAMP, \
    KDT_SELECT_INT, KDT_SELECT_CHAR, storagize, ACT_NEW_RECORD, ACT_CLEAR, ACT_SUBMIT, KQV_EMAIL, ACT_CHECK_ALL, \
    ACT_UNCHECK_ALL, KQV_GROUP_ID
from m16e.ktfact import KTF_COL_ORDER, KTF_SORTABLE_COLS, KTF_CELL_CLASS, \
    KTF_COLS, KTF_TITLE, KTF_TYPE, \
    KTF_CELL_LINK, KTF_LINK_C, KTF_LINK_F, KTF_ARGS, KTF_ARGS_F, \
    KTF_BUTTONS, KTF_NAME, KTF_VALUE, KTF_OPTIONS, KTF_ID, KTF_CSS_CLASS, KTF_ONCLICK, K_CHK_ID_PREFIX, KTF_CHECKBOXES, \
    KTF_CHECKBOX_ID
from m16e.table_factory_with_session import extract_ids_from_vars
from m16e.views.plastic_view import BaseListPlasticView


KQV_MAIL_QUEUE_ID = KQV_PREFIX + 'mail_queue_id'
ACT_ADD_ALL = 'act_add_all'
ACT_CLEAR_LIST = 'act_clear_list'
ACT_REMOVE_CHECKED = 'act_remove_checked'
MR_DIV_ID = 'mail_recipient_div'

class MailRecipientListView( BaseListPlasticView ):
    controller_name = 'mail_queue'
    function_name = 'list_recipients'


    def __init__( self, db ):
        super( MailRecipientListView, self ).__init__( db )

        T = current.T
        self.table_model = db_tables.get_table_model( 'mail_recipient', db=db )

        self.list_title = T( 'Recipient list' )

        self.append_var( KQV_MAIL_QUEUE_ID, fld_type=KDT_INT )
        self.append_var( KQV_GROUP_ID, fld_type=KDT_INT )
        self.append_var( KQV_EMAIL, fld_type=KDT_CHAR )
#        term.printDebug( 'query_vars: %s' % repr( self.query_vars ) )

        self.content_div_id = MR_DIV_ID
        self.nav.width = 3
        self.print_query = True


    def get_inhibit_actions( self ):
        return [ ACT_NEW_RECORD, ACT_CLEAR ]


    def get_table_view_dict( self ):
        T = current.T
        tdef = { KTF_COL_ORDER: [ 'id', 'email', 'sent', 'status' ],
                 KTF_SORTABLE_COLS: [ 'id', 'email', 'sent', 'status' ],
                 KTF_CELL_CLASS: 'table_border',
                 KTF_COLS: { 'id': { KTF_TITLE: T( 'Id' ),
                                     KTF_TYPE: KDT_INT,
                                     # KTF_CELL_LINK: { KTF_LINK_C: self.controller_name,
                                     #                  KTF_LINK_F: 'edit',
                                     #                  KTF_ARGS_F: [ 'id' ]
                                     #                  },
                                     KTF_CELL_CLASS: 'table_border',
                                     },
                             'mail_queue_id': { KTF_TITLE: T( 'Mail_queue_id' ),
                                                KTF_TYPE: KDT_INT,
                                                KTF_CELL_CLASS: 'table_border',
                                                },
                             'email': { KTF_TITLE: T( 'Email' ),
                                        KTF_TYPE: KDT_CHAR,
                                        KTF_CELL_CLASS: 'table_border',
                                        },
                             'sent': { KTF_TITLE: T( 'Sent' ),
                                       KTF_TYPE: KDT_TIMESTAMP,
                                       KTF_CELL_CLASS: 'table_border',
                                       },
                             'status': { KTF_TITLE: T( 'Status' ),
                                         KTF_TYPE: KDT_CHAR,
                                         KTF_CELL_CLASS: 'table_border',
                                         },
                             },
                 KTF_CHECKBOXES: [ { KTF_NAME: K_CHK_ID_PREFIX + '%d',
                                     KTF_CHECKBOX_ID: 'id',
                                     KTF_TITLE: T( 'Select' ) },
                                   ],
                 }
        self.tdef = storagize( tdef )
        return self.tdef

    
    def get_table_qdata_dict( self, extra_buttons={} ):
        T = current.T
        db = self.db
        if not self.qdata:
            jq_check_all = '''
                jQuery( '#%s input[name^="%s"]' ).attr( 'checked', true ); return false;
                ''' % ( MR_DIV_ID, K_CHK_ID_PREFIX )
            jq_uncheck_all = '''
                jQuery( '#%s input[name^="%s"]' ).attr( 'checked', false ); return false;
                ''' % ( MR_DIV_ID, K_CHK_ID_PREFIX )
            g_list = db( db.auth_group.id > 0).select( orderby='role' )
            g_options = [ (g.id, T( g.role )) for g in g_list ]
            g_options.insert( 0, (0, '') )
            qdata = { KTF_BUTTONS: [ { KTF_NAME: 'action',
                                       KTF_TITLE: T( 'Add all' ),
                                       KTF_ID: 'bt_add_all',
                                       KTF_VALUE: ACT_ADD_ALL,
                                       KTF_CSS_CLASS: 'btn btn-primary' },
                                     { KTF_NAME: 'action',
                                       KTF_TITLE: T( 'Remove checked' ),
                                       KTF_ID: 'bt_remove_checked',
                                       KTF_VALUE: ACT_REMOVE_CHECKED,
                                       KTF_CSS_CLASS: 'btn btn-warning' },
                                     { KTF_NAME: 'action',
                                       KTF_TITLE: T( 'Clear list' ),
                                       KTF_ID: 'bt_clear_list',
                                       KTF_VALUE: ACT_CLEAR_LIST,
                                       KTF_CSS_CLASS: 'btn btn-primary' },
                                     { KTF_NAME: 'action',
                                       KTF_TITLE: T( 'Check all' ),
                                       KTF_VALUE: ACT_CHECK_ALL,
                                       KTF_ONCLICK: jq_check_all,
                                       KTF_CSS_CLASS: 'btn btn-info' },
                                     { KTF_NAME: 'action',
                                       KTF_TITLE: T( 'Uncheck all' ),
                                       KTF_VALUE: ACT_UNCHECK_ALL,
                                       KTF_ONCLICK: jq_uncheck_all,
                                       KTF_CSS_CLASS: 'btn btn-info' },
                                     ],
                      KTF_COL_ORDER: [ KQV_EMAIL, KQV_GROUP_ID ],
                      KTF_COLS: { KQV_EMAIL: { KTF_TITLE: T( 'Email' ),
                                               KTF_TYPE: KDT_CHAR, },
                                  KQV_GROUP_ID: { KTF_TITLE: T( 'Group' ),
                                                  KTF_TYPE: KDT_SELECT_INT,
                                                  KTF_OPTIONS: g_options },
                                  },
                      }
            self.qdata = storagize( qdata )
        return self.qdata


    def process_pre_validation_actions( self ):
        super(MailRecipientListView, self).process_pre_validation_actions()
        if self.action:
            if self.action == ACT_ADD_ALL:
                self.add_all()
            elif self.action == ACT_CLEAR_LIST:
                self.clear_list()
            elif self.action == ACT_REMOVE_CHECKED:
                self.remove_checked()
            else:
                super( MailRecipientListView, self ).process_pre_validation_actions()


    def get_query_select( self ):
        query = '''
            select
                mr.* 
        '''
        return query


    def get_query_from( self ):
        query_form = '''
            from mail_recipient mr '''
        if self.query_vars.get( KQV_GROUP_ID ):
            query_form += '''
                join auth_user au on au.email = mr.email
                join auth_membership am on au.id = am.user_id
            '''
        return query_form


    def get_query_data( self, orderby=None ):
        qd = super( MailRecipientListView, self ).get_query_data( orderby )
        qv_mail_queue_id =  self.query_vars.get( KQV_MAIL_QUEUE_ID )
        if qv_mail_queue_id:
            qd.addAnd( QueryData( 'mail_queue_id = %(mail_queue_id)s',
                                  { 'mail_queue_id': qv_mail_queue_id } ) )
        email = self.query_vars.get( KQV_EMAIL )
        if email:
            qd.addAnd( QueryData( 'mr.email ilike( %(email)s )',
                                  { 'email': '%%' + email + '%%' } ) )

        group_id = self.query_vars.get( KQV_GROUP_ID )
        if group_id:
            qd.addAnd( QueryData( 'am.group_id = %(group_id)s',
                                  { 'group_id': group_id } ) )
        term.printDebug( repr( qd ) )
        return qd


    def parse_request_vars( self, post_vars=None, get_vars=None ):
        super( MailRecipientListView, self ).parse_request_vars( post_vars, get_vars )
        T = current.T
        db = self.db
        qv_mail_queue_id =  self.query_vars.get( KQV_MAIL_QUEUE_ID )
        if qv_mail_queue_id:
            mq_model = db_tables.get_table_model( 'mail_queue', db=db )
            mq = mq_model[ qv_mail_queue_id ]
            # self.list_subtitle = A( T( 'Subject' ),
            #                         ': ' + mq.subject + ' (',
            #                         mq.when_to_send.strftime( '%Y-%m-%d %H:%M' ),
            #                         ')',
            #                         _href=URL( c=self.controller_name,
            #                                    f='edit',
            #                                    args=[ qv_mail_queue_id ] ) )


    def post_process( self, div_content ):
        super( MailRecipientListView, self ).post_process( div_content )
        db = self.db
        qv_mail_queue_id =  self.query_vars.get( KQV_MAIL_QUEUE_ID )
        if qv_mail_queue_id:
            mq_model = db_tables.get_table_model( 'mail_queue', db=db )
            mq = mq_model[ qv_mail_queue_id ]
            return self.set_result( dict( mail_queue=mq ) )

    def add_all( self ):
        db = self.db
        regex = re.compile( 'test.*@m16e.com' )
        mr_model = db_tables.get_table_model( 'mail_recipient', db=db )
        q_sql = (db.auth_user.registration_key == '')
        au_list = db( q_sql ).select( orderby='id' )
        for au in au_list:
            mo = regex.search( au.email )
            if mo:
                term.printLog( 'Skipping test mail: %s' % au.email )
                continue
            mail_queue_id = self.query_vars.get( KQV_MAIL_QUEUE_ID )
            if mail_queue_id:
                q_sql = (db.mail_recipient.mail_queue_id == mail_queue_id)
                q_sql &= (db.mail_recipient.email == au.email)
                mr = self.table_model.select( q_sql ).first()
                if not mr:
                    mr_model.insert( dict( mail_queue_id=self.query_vars.get( KQV_MAIL_QUEUE_ID ),
                                           email=au.email ) )


    def clear_list( self ):
        db = self.db
        q_sql = (db.mail_recipient.mail_queue_id == self.query_vars.get( KQV_MAIL_QUEUE_ID ))
        self.table_model.delete( q_sql )


    def remove_checked( self ):
        request = current.request
        db = self.db
        ids = extract_ids_from_vars( request.vars )
        q_sql = (db.mail_recipient.id.belongs( ids ))
        self.table_model.delete( q_sql )
