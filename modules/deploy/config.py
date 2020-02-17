# coding=utf-8


'''
config_file: {
    'w3_server_host': 'example.com',
    'w3_server_port': 22,
    'w3_server_sys_user': 'carlos',
    'w3_server_db_user': 'carlos',
    'w3_server_w3_user': 'www-data',
    'w3_server_sys_password': 'change-me',
    'w3_server_db_password': 'naosei' },
    'git_server': 't5.m16e.com',
    'git_user_name': 'Carlos Correia',
    'git_user_email': 'carlos@change-me',
    'git_gitolite_user': 'git',
    'mail_server': 'smtp.example.com:25',
    'mail_sender': 'support@example.com',
    'mail_login': 'user:password',
    'mail_tls': False,
    'local_folder': '/home/carlos/development/m16e/%(cluster_name)s',
    'database': '%(cluster_name)s__%(app_name)s',
    'theme': 'cms' },
    'user_list': [ { 'fname': 'Carlos Correia',
                     'email': 'carlos@example.com',
                     'password': 'change-me',
                     'groups': 'dev' },
                   { 'fname': 'Suporte',
                     'email': 'suporte@example.com',
                     'password': 'change-me',
                     'group': 'support' },
                 ],
}
'''

import ast
import deploy_menu
from m16e import term


class Config( object ):
    def __init__( self, config_filename ):
        super( Config, self ).__init__()
        f = open( config_filename )
        text = f.read()
        f.close()
        self.config_data = ast.literal_eval( text )
        # term.printDebug( 'data:\n%s' % repr( self.config_data ) )
        self.curr_section = deploy_menu.SEC_SERVER
        self.server = None
        self.cluster = None
        self.app = None
        self.db_compression = self.config_data.get( 'db_compression' ) or 'j'
        self.app_theme = self.config_data.get( 'app_theme' ) or 'm16e'
        self.theme_name = self.config_data.get( 'theme_name' ) or 'm16e'
        self.theme_title = self.config_data.get( 'theme_title' ) or 'Innovative Web'
        self.theme_subtitle = self.config_data.get( 'theme_subtitle' ) or 'Next Generation WepApps'
        self.theme_logo_header = self.config_data.get( 'theme_logo_header' )
        self.theme_login_button_position = self.config_data.get( 'theme_login_button_position' ) or 'header'



    def get_server( self ):
        if not self.server:
            from server import Server
            self.server = Server( self )
        return self.server


    def get_cluster( self ):
        if not self.cluster:
            from cluster import Cluster
            self.cluster = Cluster( self )
        return self.cluster


    def get_app( self ):
        if not self.app:
            from app import App
            self.app = App( self )
        return self.app


    def get_db_name( self, app_name ):
        data = { 'cluster_name': self.get_cluster().cluster_name,
                 'app_name': app_name }
        database = self.config_data.get( 'database' ) % data
        term.printDebug( 'database: %s' % (repr( database )) )
        return database
