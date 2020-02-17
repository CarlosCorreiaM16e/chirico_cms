#! /usr/bin/python
# coding=utf-8

from fabric.context_managers import settings
from fabric.contrib import files
from deploy_utils import cli_sudo_run
from gluon.storage import Storage
from m16e import term


class Server( object ):
    tag = 'server'

    def __init__( self, config, test_server=False ):
        self.config = config
        self.test_server = test_server
        self.server_status = None
        self.host = config.config_data.get( 'w3_server_host' )
        self.port = int( config.config_data.get( 'w3_server_port' ) or 22 )
        self.sys_user = config.config_data.get( 'w3_server_sys_user' )
        self.db_user = config.config_data.get( 'w3_server_db_user' )
        self.w3_user = config.config_data.get( 'w3_server_w3_user' )
        self.sys_password = config.config_data.get( 'w3_server_sys_password' )
        self.db_password = config.config_data.get( 'w3_server_db_password' )
        self.mail_server = config.config_data.get( 'mail_server' )
        self.mail_sender = config.config_data.get( 'mail_sender' )
        self.mail_login = config.config_data.get( 'mail_login' )
        self.mail_tls = config.config_data.get( 'mail_tls' )


    def get_user_host_string( self ):
        if self.port != 22:
            return '%s@%s:%d' % ( self.sys_user, self.host, self.port )
        return '%s@%s' % ( self.sys_user, self.host )


    def get_web_home_folder( self ):
        return '/home/%s' % self.w3_user


    def get_sys_home_folder( self ):
        return '/home/%s' % self.sys_user


    def get_server_status( self ):
        if not self.server_status:
            web_home_created = 'NO'
            with settings( host_string=self.get_user_host_string(),
                           password=self.sys_password ):
                web_folder = self.get_web_home_folder()
                # term.printDebug( 'web_folder: %s' % web_folder )
                if files.exists( web_folder ):
                    web_home_created = 'in %s' % web_folder

            self.server_status = Storage( server_name=self.host,
                                          web_home_created=web_home_created )
        return self.server_status


    def apache_ctl( self, action ):
        if not action in [ 'start', 'stop', 'restart' ]:
            raise Exception( 'improper action: %s' % repr( action ) )
        with settings( host_string=self.get_user_host_string(),
                       password=self.sys_password ):
            cli_sudo_run( '/etc/init.d/apache2 %s' % action,
                          password=self.sys_password )


    def get_ip( self ):
        with settings( host_string=self.get_user_host_string(),
                       password=self.sys_password ):
            cli_sudo_run( '/sbin/ifconfig',
                          password=self.sys_password )


    def pg_ctl( self, action ):
        if not action in [ 'start', 'stop', 'restart' ]:
            raise Exception( 'improper action: %s' % repr( action ) )
        with settings( host_string=self.get_user_host_string(),
                       password=self.sys_password ):
            cli_sudo_run( '/etc/init.d/postgresql %s' % action,
                          password=self.sys_password )


    def __repr__( self ):
        s = 'Server: {'
        for a in self.__dict__:
            if a == 'config':
                continue
            s += '\n    %s: %s' % (repr( a ), repr( self.__dict__[a] ) )
        s += '\n  }'
        return s




