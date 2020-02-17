# -*- coding: utf-8 -*-
import sys
import traceback

from gluon import current, URL
from gluon.storage import Storage
from m16e import term
from m16e.files import fileutils
from m16e.system import env


TX_BASE_FOLDER = 'var/run'
# MAIN_ERP_APP = 'blm_enn_erp'
# CUSTOMERS_APP = 'clientes'
# WEB_PREFIX = 'WEB-request'

# DB_ERP_PREFIX = 'enn__'
# DB_CUSTOMERS_URI = 'postgres://belmiro:naosei@localhost/%sclientes' % DB_ERP_PREFIX
# DB_ERP_URI_PREFIX = 'postgres://belmiro:naosei@localhost/' + DB_ERP_PREFIX
# DB_MAIN_ERP_URI = DB_ERP_URI_PREFIX + CUSTOMERS_APP

class TxRPC( object ):
    def __init__( self, app_name ):
        self.app_name = app_name


    def compose_line( self, k, v ):
        s = '%(key)s = %(value)s' % dict( key=k, value=v )
        return s


    def parse_line( self, line ):
        term.printDebug( 'line: %s' % repr( line ) )
        k, v = line.split( ' = ', 1 )
        return k, v


    def get_app_folder( self ):
        data = dict( web_folder=current.request.env.web2py_path,
                     tx_folder=TX_BASE_FOLDER,
                     app_name=self.app_name )
        filename = '%(web_folder)s/%(tx_folder)s/%(app_name)s' % data
        return filename

    def get_app_url( self ):
        request = current.request
        url = 'https' if request.is_https else 'http'
        url += '://'
        url += env.get_http_hostname() + '/'
        url += self.app_name + '/'
        url += 'txrpc/call/xmlrpc'
        return url


    def read_file( self, filename ):
        path = self.get_app_folder() + '/' + filename
        lines = fileutils.read_file_lines( path )
        return lines


