# -*- coding: utf-8 -*-

import datetime
import os
import sys
import traceback
from decimal import Decimal

from gluon import current
from gluon.storage import Storage
from m16e import term
from m16e.decorators import deprecated

DT=datetime.datetime
DATE=datetime.date

# unit types
UNIT_TYPE_SITE_ATTACHES = 'site-attaches'

# message types (user_message)
MSG_TYPE_FLASH = (2, 'flash')
MSG_TYPE_RESPONSE = (1, 'response')
MSG_TYPE_SET = { MSG_TYPE_RESPONSE[0]: MSG_TYPE_RESPONSE[1],
                 MSG_TYPE_FLASH[0]: MSG_TYPE_FLASH[1] }

# roles
K_ROLE_ADMIN = 'admin'
K_ROLE_DEVELOPER = 'dev'
K_ROLE_EDITOR = 'editor'
# K_ROLE_ERP = 'erp'
K_ROLE_MANAGER = 'manager'
K_ROLE_SUPPORT = 'support'
K_ROLE_USER = 'user'

#----------------------------------------------------------------------
K_MAIN_ERROR_PANEL = 'main_error_panel'

#----------------------------------------------------------------------
# data types
KDT_CHAR = 'char'
KDT_BLOB_IMG = 'blob_img'
KDT_BLOB_MEDIA = 'blob_media'
KDT_BOOLEAN = 'boolean'
KDT_INT = 'int'
KDT_INT_LIST = KDT_INT + '_list'
KDT_DATE = 'date'
KDT_DEC = 'dec'
KDT_FILE = 'file'
KDT_MONEY = 'money'
KDT_PERCENT = 'percent'
KDT_RAW = 'raw'
KDT_SPECIAL = 'special'
KDT_TIME = 'time'
KDT_TIMESTAMP = 'timestamp'
KDT_TIMESTAMP_PRETTY = 'timestamp_pretty'
KDT_XML = 'xml'

KDT_SELECT_INT = 'select_int'
KDT_SELECT_CHAR = 'select_char'

#----------------------------------------------------------------------
'''
Query prefixes:

qv_: url variables
qk_: url constants

Query suffixes:
__return: return values
'''
# query vars
KQV_PREFIX = 'qv_'
KQR_SUFFIX = '__return'

KQV_ARGS_NAME = KQV_PREFIX + 'args_name'
KQV_ARGS_SHOW_ALL = KQV_PREFIX + 'args_show_all'

KQV_URL_C = KQV_PREFIX + 'url_c'
KQV_URL_F = KQV_PREFIX + 'url_f'
KQV_URL_ARGS_F = KQV_PREFIX + 'url_args_f'
KQV_URL_ARGS_V = KQV_PREFIX + 'url_args_v'
KQV_URL_VARS_F = KQV_PREFIX + 'url_vars_f'
KQV_URL_VARS_V = KQV_PREFIX + 'url_vars_v'
KQV_RETURN_NAME = KQV_PREFIX + 'return_name'

#----------------------------------------------------------------------
# return vars
KQR_SELECTED_ID = KQV_PREFIX + 'selected_id' + KQR_SUFFIX

#----------------------------------------------------------------------
# list vars
KQV_LIMIT = KQV_PREFIX + 'limit'
KQV_OFFSET = KQV_PREFIX + 'offset'
KQV_ORDER = KQV_PREFIX + 'order'
KQV_NEXT_C = 'next_c'
KQV_NEXT_F = 'next_f'
KQV_NEXT_ARGS = 'next_args'

KQV_COMMON_LIST_VARS = [ KQV_LIMIT, KQV_OFFSET, KQV_ORDER ]

KQV_TITLE = 'qv_title'

KQV_SHOW_ALL = 'qv_show_all'
KQV_SHOW_DEACTIVATED = 'qv_show_deactivated'

# attach types
ATT_TYPE_IMAGES = 'images'
KQV_PAGE_SIZE = KQV_PREFIX + 'page_size'
KQV_BLOCK_SIZE = KQV_PREFIX + 'block_size'
KQV_THUMB_SIZE = KQV_PREFIX + 'thumb_size'

KQV_UPLOAD_FILE = KQV_PREFIX + 'upload_file'
KQV_IS_SITE_IMAGE = KQV_PREFIX + 'is_site_image'


# standard actions
ACT_ADD_USER = 'act_add_user'
ACT_BACK = 'act_back'
ACT_CHECK_ALL = 'act_check_all'
ACT_CLEAR = 'act_clear'
ACT_CLEAR_SELECTION = 'act_clear_selection'
ACT_DELETE = 'act_delete'
ACT_DELETE_ALL_CHECKED = 'act_delete_all_checked'
ACT_DELETE_RECORD = 'act_delete_record'
ACT_EDIT_GROUP = 'act_edit_group'
ACT_MOVE_ALL_CHECKED = 'act_move_all_checked'
ACT_NEW_IMAGE = 'act_new_image'
ACT_NEW_MEDIA = 'act_new_media'
ACT_NEW_RECORD = 'act_new_record'
ACT_PASTE = 'act_paste'
ACT_PURGE = 'act_purge'
ACT_SEND_MAIL = 'act_send_mail'
ACT_SEND_MESSAGE = 'act_send_message'
ACT_SEND_PASSWORD_RECOVER = 'act_send_password_recover'
ACT_SELECT_ALL_CHECKED = 'act_select_all_checked'
ACT_SUBMIT = 'act_submit'
ACT_SUBMIT_USER = 'act_submit_user'
ACT_UNCHECK_ALL = 'act_uncheck_all'
ACT_UPLOAD_FILE = 'act_upload_file'

#----------------------------------------------------------------------
# query constants
KQK_PREFIX = 'qk_'
KQK_URL_C = KQK_PREFIX + 'c'
KQK_URL_F = KQK_PREFIX + 'f'

KQK_AUTH_USER_ID = KQK_PREFIX + 'auth_user_id'
KQV_EMAIL = KQV_PREFIX + 'email'
KQV_NAME = KQV_PREFIX + 'name'
KQV_GROUP_ID = KQV_PREFIX + 'group_id'

# bootstrap 3 defs
TAB_TOP_DIV_CLASS = 'panel with-nav-tabs panel-default'
TAB_HEADER_DIV_CLASS = 'panel-heading'
TAB_UL_CLASS = 'nav nav-tabs'
TAB_BODY_DIV_CLASS = 'panel-body'
TAB_CONTENT_DIV_CLASS = 'tab-content'
TAB_PANE_CLASS = 'tab-pane fade'
TAB_UL_ROLE = 'tablist'
TAB_ROLE = 'tab'

#------------------------------------------------------------------
# defaults to XML()
HTML_PERMITED_TAGS = [ 'a',
                       'b',
                       'blockquote',
                       'br/',
                       'i',
                       'li',
                       'ol',
                       'ul',
                       'p',
                       'cite',
                       'code',
                       'pre',
                       'img/']
HTML_ALLOWED_ATTRIBUTES = { 'a': ['href', 'title'],
                           'img': ['src', 'alt'],
                           'blockquote': ['type'] }

#------------------------------------------------------------------
TX_ERROR_NONE = 0
TX_ERROR_OTHER = -1
TX_ERROR_ENT_NIF_INVALID = -101
TX_ERROR_ENT_ZIP_CODE_INVALID = -102

#------------------------------------------------------------------
DECIMAL_0 = Decimal( 0 )
DECIMAL_1 = Decimal( 1 )
DECIMAL_100 = Decimal( 100 )

#------------------------------------------------------------------
NAV_DIR_NEXT = 'next'
NAV_DIR_PREV = 'prev'
NAV_DIR_SET = (NAV_DIR_PREV, NAV_DIR_NEXT)

#------------------------------------------------------------------
def storagize( d ):
    '''Converts dict to Storage()

    storagize( {
        'd1': [
            {'op1': 'i1', 'op2': 'v1'},
            {'op1': 'i2', 'op2': 'v2'} ],
        'cols': {
            'col1': { 'title': 'Title 1', 'value': 'Value 1'    },
            'col2': { 'title': 'Title 2', 'value': 'Value 2' },
        },
    } )
    <Storage {
        'cols': <Storage {
            'col2': <Storage { 'value': 'Value 2', 'title': 'Title 2'}>,
            'col1': <Storage {'value': 'Value 1', 'title': 'Title 1'}>
        }>,
        'd1': [
            <Storage {'op1': 'i1', 'op2': 'v1'}>,
            <Storage {'op1': 'i2', 'op2': 'v2'}>
        ]
    }>

    >>> storagize( { 'd1': [ {'op1': 'i1', 'op2': 'v1'}, {'op1': 'i2', 'op2': 'v2'} ], 'cols': { 'col1': { 'title': 'Title 1', 'value': 'Value 1'    }, 'col2': { 'title': 'Title 2', 'value': 'Value 2' }, }, } )
    <Storage {'cols': <Storage {'col2': <Storage {'value': 'Value 2', 'title': 'Title 2'}>, 'col1': <Storage {'value': 'Value 1', 'title': 'Title 1'}>}>, 'd1': [<Storage {'op1': 'i1', 'op2': 'v1'}>, <Storage {'op1': 'i2', 'op2': 'v2'}>]}>

    '''

#    term.printLog( 'd: %s' % repr( d ) )
    td_type = str( type( d ) )
    sd_type = td_type.split( "'" )[1]
    d_type = sd_type.split( '.' )[-1]
    if not d or d_type in ['Row', 'Reference']:
        return d
#    term.printLog( 'd: %s' % repr( d ) )

    if not type( d ) is Storage:
        if hasattr( d, 'append' ):
            list = []
            for el in d:
                list.append( storagize( el ) )
            return list

    if hasattr( d, 'keys' ):
#        term.printLog( 'd: %s' % repr( d ) )
        s = Storage( d )
        for e in s:
#            term.printLog( 's[%s]: %s (type: %s)' % ( e, repr( s[e] ), type( s[e] ) ) )
            if hasattr( s[e], 'keys' ) or \
                 hasattr( s[e], 'append' ):
                s[e] = storagize( s[e] )
#        term.printLog( 's: %s' % repr( s ) )
        return s

    return d

#------------------------------------------------------------------
def get_wday( day ):
    '''
    in python week days start at Monday
    in PG start at Saturday
    '''
    dt_wday = day.weekday() + 2
    if dt_wday > 6:
        dt_wday -= 7
    return dt_wday

#----------------------------------------------------------------------
def is_sequence( value ):
    is_seq = ( value and
               not isinstance( value, dict ) and
               ( not hasattr( value, 'strip') and
                 hasattr( value, '__getitem__' ) and
                 hasattr( value, '__iter__' ) ) )
    return is_seq


def format_exception( e ):
    exception_list = traceback.format_stack()
    exception_list = exception_list[:-2]
    exception_list.extend( traceback.format_tb( sys.exc_info()[2] ) )
    exception_list.extend( traceback.format_exception_only( sys.exc_info()[0],
                                                            sys.exc_info()[1] ) )

    exception_str = "Traceback (most recent call last):\n"
    exception_str += "".join( exception_list )
    # Removing the last \n
    exception_str = exception_str[:-1]

    return exception_str

#----------------------------------------------------------------------
def get_obj_from_current( obj_name, raise_exception=True ):
    try:
        obj = current[ obj_name ]
    except TypeError:
        t, v, tb = sys.exc_info( )
        traceback.print_exception( t, v, tb )
        obj = None
        if raise_exception:
            raise
    return obj


#----------------------------------------------------------------------
def get_init_config_data( mod_name ):
    request = current.request
    init = '%(src)s/applications/%(app)s/private/%(mod)s.py' % {
        'src': request.global_settings.applications_parent,
        'app': request.application,
        'mod': mod_name }
    if not os.path.isfile( init ):
        init = '%(src)s/applications/%(app)s/resources/config/init/%(mod)s.py' % {
            'src': request.global_settings.applications_parent,
            'app': request.application,
            'mod': mod_name }
    from m16e.files import fileutils
    init_cfg_init_data = storagize( fileutils.read_data_file( init ) )
    return init_cfg_init_data.get( mod_name )


TEST_MATCH_EQ = 1
TEST_MATCH_DIFF = 0

TEST_MATCH_LIST = [ ( TEST_MATCH_EQ, '=' ),
                    ( TEST_MATCH_DIFF, '!=' ),
                ]

def get_test_match( test_match_id ):
    for t in TEST_MATCH_LIST:
        if t[0] == test_match_id:
            return t[1]
    return ''

def get_age( birth_date ):
    now = DATE.today()
    if birth_date:
        age = now.year - birth_date.year - ( (now.month, now.day) < (birth_date.month, birth_date.day) )
        return age


def get_age_in_days( ts ):
    now = DATE.today()
    if isinstance( ts, datetime.datetime ):
        ts = ts.date()
    dif = now - ts
    return dif.days


def is_same_day( dt1, dt2 ):
    val = (dt1.year == dt2.year and dt1.month == dt2.month and dt1.day == dt2.day)
    return val


def get_ticket_data( app, ticket ):
    term.printDebug( 'ticket: %s' % repr( ticket ) )
    request = current.request
    folder = request.folder.rsplit( '/', 2 )[0] + '/' + app
    # term.printDebug( 'folder: %s' % folder )
    filename = folder + '/errors/' + ticket.split( '/', 1 )[1]
    # term.printDebug( 'filename: %s' % filename )
    from m16e.files import fileutils
    lines = fileutils.read_file_lines( filename )
    description = ''
    for l in lines:
        if l.startswith( 'S"<type' ):
            description = l.split( '>' )[1][:-1]
        elif l.startswith( "S'Traceback" ):
            # term.printDebug( 'l: %s' % l )
            tlines = l.split( '\\n' )
            # term.printDebug( 'tlines: %s' % repr( tlines ) )
            stack_trace = '\n'.join( tlines[1:] )
    return description, stack_trace


def get_new_id_from_list( old_id, id_list, idx=0 ):
    # term.printDebug( 'old_id (%s): %s' % (type( old_id ), repr( old_id ) ) )
    for i in id_list:
        if i[idx] == old_id:
            return i[ int( not idx ) ]
    term.printDebug( 'old_id NOT FOUND(%s): %s' % (type( old_id ), repr( old_id )) )
    # term.printDebug( 'id_list: %s' % repr( id_list ) )
    # raise Exception( 'old_id NOT FOUND: %s' % repr( old_id ) )
    return None


def to_utf8( s ):
    return s.decode( 'utf8' )
