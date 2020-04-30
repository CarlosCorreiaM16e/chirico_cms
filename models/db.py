# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

import datetime
import os.path
from gluon import current
from gluon.contrib.appconfig import AppConfig
from gluon.storage import Storage
from gluon.tools import Auth, Crud, Service, PluginManager
from gluon.validators import IS_EMAIL, Validator
from m16e import htmlcommon, term
from m16e.files import fileutils
from m16e.system import env
from m16e.system.env import DEV_SERVERS
# from m16e.ui import ui_factory

if 0:
    import gluon
    from gluon.dal import Field
    from gluon.validators import CRYPT
    import gluon.languages.translator as T
    global request; request = gluon.globals.Request()
    global DAL; DAL = gluon.dal()
    global response; response = gluon.globals.Response()

if request.global_settings.web2py_version < "2.14.1":
    raise HTTP(500, "Requires web2py 2.13.3 or newer")

current.server_name = env.get_server_name()
current.http_protocol = 'https' if request.is_https else 'http'
current.remote_ip = str( request.wsgi.environ[ 'REMOTE_ADDR' ] ) if request.wsgi else ''

app_config = AppConfig()
uri = app_config.take('db.uri')
db_name = uri.split( '/' )[-1]
term.printLog( 'db_name: %s' % db_name )
db = DAL( uri,
          pool_size=app_config.take( 'db.pool_size', cast=int ),
          check_reserved=['postgres'] )

formstyle = app_config.take('forms.formstyle')
if formstyle:
    response.formstyle = formstyle
form_label_separator = app_config.take('forms.separator')
if form_label_separator:
    response.form_label_separator = form_label_separator

v_info = fileutils.get_package_version_info( request.folder )

response.meta.version_id = '%(major)s.%(minor)s.%(revision)s' % (v_info)
response.meta.version_date = htmlcommon.format_date( v_info[ 'date' ] )

if not request.is_local:
    session.secure()

term.printLog( '''
    HTTP_HOST: %(HTTP_HOST)s
    PATH_INFO: %(PATH_INFO)s
    args: %(args)s
    vars: %(vars)s
    SERVER_NAME: %(SERVER_NAME)s
    REMOTE_ADDR: %(REMOTE_ADDR)s
    folder: %(folder)s
    WEB2PY_PATH: %(WEB2PY_PATH)s
    protocol: %(protocol)s
    local: %(local)s
    user_agent: %(user_agent)s
    user_agent_dict: %(user_agent_dict)s
    ''' % { 'HTTP_HOST': env.get_http_hostname(),
            'PATH_INFO': env.get_path_info(),
            'args': repr( request.args ),
            'vars': repr( request.vars.keys() ),
            'SERVER_NAME': current.server_name,
            'REMOTE_ADDR': current.remote_ip,
            'folder': request.folder,
            'WEB2PY_PATH': request.env.web2py_path,
            'protocol': 'https' if request.is_https else 'http',
            'local': request.is_local,
            'user_agent': request.env.http_user_agent,
            'user_agent_dict': request.user_agent()
            } )

current.is_testing = os.path.isfile( 'TESTING' )
# term.printLog( '>>> testing: %s' % current.is_testing )
current.hostname = app_config.take( 'host.hostname' )
# term.printLog( '>>> hostname: %s' % current.hostname )
url_protocol = 'https' if request.is_https else 'http'

# term.printLog( 'dbUrl: ' + dbUrl )

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
# response.generic_patterns = ['*'] if request.is_local else []
## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

auth = Auth(db, hmac_key=Auth.get_or_create_key())
crud, service, plugins = Crud(db), Service(), PluginManager()

T.force( session.lang or app_config.get( 'language', 'pt-pt' ) )

auth.settings.create_user_groups = None
auth.settings.password_min_length = 8

db.define_table( auth.settings.table_user_name,
                 Field( 'first_name', length=128, notnull=True, label = T( 'Full name' ) ),
                 Field( 'last_name', length=128, default='_', notnull=True,
                        readable = False, writable = False ),
                 Field( 'email', length=128, default='', unique=True, notnull=True ),
                 Field( 'password', 'password', length=512,                        # required
                        readable=False, label=T( 'Password (min. 8 char.)' ),
                        requires = CRYPT( min_length = auth.settings.password_min_length ) ),
                 Field( 'registration_key', length=512,                                # required
                        writable=False, readable=False, default=''),
                 Field( 'reset_password_key', length=512,                            # required
                        writable=False, readable=False, default=''),
                 Field( 'registration_id', length=512,                                 # required
                        writable=False, readable=False, default=''),
                 Field( 'ctime', 'datetime', default = datetime.datetime.now(), notnull = True,
                        readable = False, writable = False ),
                 migrate=False
                 )


auth.define_tables( migrate=False )

class TEST_LOWER( Validator ):
    """
    test lower case

    >>> TEST_LOWER()('ABC')
    ('abc', 'Must be lowercase)
    >>> TEST_LOWER()('abd')
    ('abc', None)
    """
    g_count = 0

    def __init__( self ):
        self.l_count = 0

    def __call__(self, value):
#         term.printDebug( 'count: (g: %d; l: %d)' % (self.g_count, self.l_count) )
        self.g_count += 1
        self.l_count += 1
        domain = value.split( '@' )[1]
        if not domain.islower():
            return (value, T( 'Domain (after "@") must be lowercase' ))
        return (value, None)


db.auth_user.email.requires = [ IS_EMAIL(), TEST_LOWER() ]

current.db_model_list = Storage()

## configure email
mail = auth.settings.mailer
if not current.server_name or current.server_name in DEV_SERVERS:
    mail.settings.server = 'logging'
else:
    mail.settings.server = app_config.take( 'smtp.server' )

mail.settings.sender = app_config.take( 'smtp.sender' )
mail.settings.login = app_config.take( 'smtp.login' )
mail.settings.tls = (app_config.take( 'smtp.tls' ).lower() in [ 'true', 'yes' ] )
# if current.is_testing:
#     mail.settings.server = 'logging'

## configure auth policy
auth.settings.login_after_registration = False
auth.settings.registration_requires_verification = True
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

current.db = db
current.table_models = Storage()

from m16e.db import db_tables

import m16e.db.list_of_tables
db_tables.register_table_list( db, table_list=m16e.db.list_of_tables.TABLE_LIST )
import chirico.db.list_of_tables
db_tables.register_table_list( db, table_list=chirico.db.list_of_tables.TABLE_LIST )
import forum_threads.db.list_of_tables
db_tables.register_table_list( db, table_list=forum_threads.db.list_of_tables.TABLE_LIST )

current.auth = auth
current.mail = mail
current.app_name = request.application
current.meta_name = 'CHIRICO'
current.app_folder = request.folder
current.currency = Storage( symbol=app_config.take('app.currency_symbol') )
current.app_config = app_config
current.app_config_data = None

current.login_field = current.app_config.take( 'app.login' ) or 'email'
current.qt_decimals = 2
current.currency_decimals = 2

# term.printDebug( 'response.meta: %s' % repr( response.meta ) )

if request.wsgi:
    from chirico.app import app_factory
    from chirico.db import page_stats
    response.meta.flash_msg_delay = app_factory.get_flash_msg_delay()
    response.meta.app_theme = app_factory.get_app_theme()
    response.meta.use_bootstrap_select = current.app_config.get( 'ui.bootstrap_select', default=False )
    if env.get_path_info():
        page_stats.update_page_log( db=db )

