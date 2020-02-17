# coding=utf-8

import os
from fabric.context_managers import settings, cd, lcd
from fabric.contrib import files
from fabric.operations import put

from deploy_utils import cli_run, cli_sudo_run
from gluon.storage import Storage
from m16e import term


class Cluster( object ):
    tag = 'cluster'

    def __init__( self, config ):
        self.config = config
        self.server = config.get_server()
        self.cluster_name = self.config.config_data.get( 'cluster_name' )
        self.base_folder = 'sites/%(cluster_name)s'
        self.cluster_status = None
        self.web2py_release = self.config.config_data.get( 'web2py_release' )
        self.web2py_zip = self.config.config_data.get( 'web2py_zip' ) % dict( web2py_release=self.web2py_release )
        self.repo_folder = self.config.config_data.get( 'w2p_git_repo' ) % dict( cluster_name=self.cluster_name )


    def get_abs_w3_folder( self ):
        server = self.config.get_server()
        home_folder = server.get_web_home_folder()
        # term.printDebug( 'self.base_folder: %s' % repr( self.base_folder ) )
        base_folder = self.base_folder % { 'cluster_name': self.cluster_name }
        # term.printDebug( 'base_folder: %s' % repr( base_folder ) )
        abs_folder = '%s/%s' %(home_folder, base_folder)
        # term.printDebug( 'abs_folder: %s' % repr( abs_folder ) )
        return abs_folder


    def get_abs_w2p_folder( self ):
        abs_folder = self.get_abs_w3_folder() + '/web2py'
        # term.printDebug( 'abs_folder: %s' % repr( abs_folder ) )
        return abs_folder


    def get_abs_w2p_repo_folder( self ):
        abs_w2p_repo_folder = '%s/web2py/releases/%s' % (self.get_abs_repo_folder(),
                                                         self.web2py_release)
        return abs_w2p_repo_folder


    def get_abs_repo_folder( self ):
        server = self.server
        return '/'.join( (server.get_sys_home_folder(),
                          self.repo_folder) )


    def get_cluster_status( self, refresh=False ):
        if not self.cluster_status or refresh:
            server = self.config.get_server()
            with settings( host_string=server.get_user_host_string(),
                           password=server.sys_password ):
                self.cluster_status = Storage( cluster_name=self.cluster_name)
                w2p_web_folder = self.get_abs_w2p_folder()
                # term.printDebug( 'w2p_folder: %s' % repr( w2p_web_folder ) )
                if files.exists( w2p_web_folder ):
                    self.cluster_status.w2p_web_folder_created = 'in ' + w2p_web_folder
                else:
                    self.cluster_status.w2p_web_folder_created = 'NO'

        return self.cluster_status


    def init_web2py_from_zip( self ):
        # term.printDebug( 'cluster_name: %s' % self.cluster_name )
        server = self.config.get_server()
        with settings( host_string=server.get_user_host_string(),
                       password=server.sys_password ):
            # abs_w2p_repo_folder = '%s/web2py/releases/%s' % (self.get_abs_repo_folder(),
            #                                                  self.web2py_release)
            abs_w2p_repo_folder = self.get_abs_w2p_repo_folder()
            term.printDebug( 'abs_w2p_repo_folder: %s' % abs_w2p_repo_folder ) #, prompt_continue=True )

            if files.exists( abs_w2p_repo_folder ):
                return 'ERROR:-> REPO EXISTS: %s' % abs_w2p_repo_folder

            zip_path = self.web2py_zip
            zip_file = self.web2py_zip.split('/')[-1]
            if not files.exists( 'tmp/%s' % zip_file ):
                put( zip_path, 'tmp' )
            term.printDebug( 'zip_file: %s' % zip_file )
            parent_folder, app_folder = abs_w2p_repo_folder.rsplit( '/', 1 )
            cli_run( 'mkdir -p %s' % parent_folder,
                     prompt=True,
                     print_trace=True)
            with cd( parent_folder ):
                cli_run( 'unzip ~/tmp/%(zip)s' %
                         { 'zip': zip_file },
                         prompt=True,
                         print_trace=True )
                return 'Repo created in: %s' % parent_folder


    def init_web2py( self ):
        # term.printDebug( 'cluster_name: %s' % self.cluster_name )
        abs_w2p_folder = self.get_abs_w2p_folder()
        abs_w2p_folder += '-%s' % self.web2py_release
        # term.printDebug( 'abs_w2p_repo_folder: %s' % abs_w2p_folder )
        abs_w2p_web_folder = self.get_abs_w2p_folder()
        # abs_w2p_repo_folder = '%s/web2py/releases/%s' % (self.get_abs_repo_folder(),
        #                                                  self.web2py_release)
        abs_w2p_repo_folder = self.get_abs_w2p_repo_folder()
        term.printDebug( 'abs_w2p_web_folder: %s' % abs_w2p_web_folder )
        # data = { 'p': abs_w2p_web_folder,
        #          'v': self.web2py_release }
        # abs_w2p_rel_folder = '%(p)s/releases/web2py-%(v)s' % data
        server = self.config.get_server()
        with settings( host_string=server.get_user_host_string(),
                       password=server.sys_password ):
            if files.exists( abs_w2p_web_folder ):
                return 'ERROR:-> REPO EXISTS: %s' % abs_w2p_web_folder

        # w2p_tag = self.get_w2p_tag()
        with settings( host_string=server.get_user_host_string(),
                       password=server.sys_password ):
            term.printDebug( 'abs_w2p_repo_folder: %s' % repr( abs_w2p_repo_folder ) )
            cli_sudo_run( 'mkdir -p %s/releases/%s' % (abs_w2p_web_folder,
                                                       self.web2py_release),
                          user=server.w3_user,
                          password=server.sys_password,
                          prompt=True )
            with cd( abs_w2p_web_folder ):
                with cd( 'releases/%s' % self.web2py_release ):
                    cli_sudo_run( 'pwd',
                                  password=server.sys_password )
                    cli_sudo_run( 'cp -R %s/* .' % abs_w2p_repo_folder,
                                  user=server.w3_user,
                                  password=server.sys_password,
                                  prompt=True )
                    cli_sudo_run('cp handlers/wsgihandler.py .',
                                 user=server.w3_user,
                                 password=server.sys_password,
                                 prompt=True)
                    cli_sudo_run( 'touch HOSTNAME',
                                  user=server.w3_user,
                                  password=server.sys_password,
                                  prompt=True )
                    files.append( 'HOSTNAME', server.host, use_sudo=True )

                cli_sudo_run( 'pwd',
                              user=server.w3_user,
                              password=server.sys_password,
                              prompt=True )
                cli_sudo_run( 'rm -f current',
                              user=server.w3_user,
                              password=server.sys_password,
                              prompt=True )
                cli_sudo_run( 'ln -s releases/%s current' % self.web2py_release,
                              user=server.w3_user,
                              password=server.sys_password,
                              prompt=True )
                term.printDebug( 'concluded' ) # , prompt_continue=True )
        return ''


    def drop_web2py( self ):
        # term.printDebug( 'cluster_name: %s' % self.cluster_name )
        abs_web_base_folder = self.get_abs_w2p_folder()
        abs_repo_base_folder = self.get_abs_repo_folder()
        server = self.server
        with settings( host_string=server.get_user_host_string(),
                       password=server.sys_password ):
            cli_sudo_run( 'rm -rf %s' % abs_web_base_folder,
                          # user=server.w3_user,
                          password=server.sys_password,
                          prompt=True,
                          print_trace=True )
            cli_run( 'rm -rf %s' % abs_repo_base_folder,
                     prompt=True,
                     print_trace=True )


    def drop_site_available( self ):
        server = self.server
        with settings( host_string=server.get_user_host_string(),
                       password=server.sys_password ):
            with cd( '/etc/apache2/sites-enabled' ):
                cli_sudo_run( 'rm -f %s' % (self.server_name),
                              password=server.sys_password,
                              prompt=True,
                              print_trace=True )
            with cd( '/etc/apache2/sites-available' ):
                cli_sudo_run( 'rm -f %s' % (self.server_name),
                              password=server.sys_password,
                              prompt=True,
                              print_trace=True )


    def define_web2py_admin_password( self ):
        # term.printDebug( 'cluster_name: %s' % self.cluster_name )
        w2p_folder = self.get_abs_w2p_folder()
        # term.printDebug( 'w2p_folder: %s' % repr( w2p_folder ) )
        if not w2p_folder:
            return 'No cluster defined or empty (no apps)'

        server = self.config.get_server()
        with settings( host_string=server.get_user_host_string(),
                       password=server.sys_password ):
            with cd( w2p_folder ):
                with cd( 'current' ):
                    cmd_list = [ 'python -c "from gluon.widget import console; console();"',
                                 '''python -c "from gluon.main import save_password; save_password(raw_input('admin password: '),443)" ''',
                                 'echo "disabled: True" >> applications/examples/DISABLED',
                                 'echo "disabled: True" >> applications/welcome/DISABLED'
                                 ]
                    for cmd in cmd_list:
                        cli_sudo_run( cmd,
                                      user=server.w3_user,
                                      password=server.sys_password )


    def create_site_available( self ):
        server = self.config.get_server()
        app = self.config.get_app()
        srv_name = 'w2p_%s_%s' % ( self.cluster_name,
                                   server.host.replace( '.', '_' ) )
        d = { 'server_host': server.host,
              'server_domain': '.'.join( server.host.split( '.' )[ -2: ] ),
              'server_name': srv_name,
              'srv_base_folder': self.get_abs_w2p_folder(),
              'w3_user': server.w3_user,
              'default_app': app.app_name }
        sub_domain_cfg = '''
    <VirtualHost *:80>
      ServerName %(server_host)s
      ServerDomain %(server_domain)s
      Redirect permanent / https://%(server_host)s/
    </VirtualHost>

    <VirtualHost *:443>
      ServerName %(server_host)s

      SSLEngine on
      SSLEngine on
    ''' % d
        sub_domain_cfg += '''
  SSLCertificateFile /etc/apache2/ssl/self_signed.cert
  SSLCertificateKeyFile /etc/apache2/ssl/self_signed.key
'''
        sub_domain_cfg += '''
      Header always set Strict-Transport-Security "max-age=15768000;"
      SetEnvIf User-Agent ".*MSIE.*" nokeepalive ssl-unclean-shutdown
      WSGIDaemonProcess %(server_name)s user=www-data group=www-data threads=5 processes=6
      WSGIProcessGroup %(server_name)s
      WSGIScriptAlias / %(srv_base_folder)s/current/wsgihandler.py
    ''' % d

        sub_domain_cfg += '''
      WSGIApplicationGroup %{GLOBAL}
    '''
        sub_domain_cfg += '''
      DocumentRoot %(srv_base_folder)s/current/applications/%(default_app)s

      Options +FollowSymLinks

      <Directory %(srv_base_folder)s/current/>
        AllowOverride None
        Order Allow,Deny
        Deny from all
        <Files wsgihandler.py>
          Allow from all
        </Files>
      </Directory>

      AliasMatch ^/([^/]+)/static/(?:_[\d]+.[\d]+.[\d]+/)?(.*) \
            %(srv_base_folder)s/current/applications/$1/static/$2

      <Directory %(srv_base_folder)s/current/applications/*/static/>
        Options -Indexes
        ExpiresActive On
        ExpiresDefault "access plus 1 hour"
        Order Allow,Deny
        Allow from all
      </Directory>

      #<LocationMatch ^/([^/]+)/appadmin>
      #  Deny from all
      #</LocationMatch>

      CustomLog /var/log/apache2/%(server_name)s-access.log common
      ErrorLog /var/log/apache2/%(server_name)s-error.log
    </VirtualHost>
        ''' % d

        with settings( host_string=server.get_user_host_string(),
                       password=server.sys_password ):

            src_cfg_folder = '%s/tmp' % os.path.expanduser( '~' )
            src_cfg_file = '%s/%s' % (src_cfg_folder, self.server_name)
            # term.printDebug( 'src_cfg_folder: %s' % src_cfg_folder )
            # term.printDebug( 'src_cfg_file: %s' % src_cfg_file )
            with lcd( src_cfg_folder ):
                f = open( src_cfg_file, 'w' )
                f.write( sub_domain_cfg )
                f.close()
            if not files.exists( 'tmp' ):
                cli_run( 'mkdir -p tmp' )
            put( src_cfg_file, 'tmp/%s' % self.server_name )
            remote_src_cfg_file = '/home/%s/tmp/%s' % ( server.user,
                                                        self.server_name )
            # term.printDebug( 'remote_src_cfg_folder: %s' % remote_src_cfg_file )
            cli_sudo_run( 'mv %s /etc/apache2/sites-available/' % remote_src_cfg_file,
                          password=server.sys_password )
            with cd( '/etc/apache2/sites-enabled' ):
                cli_sudo_run( 'rm -f %s' % (self.server_name),
                              password=server.sys_password )
                cli_sudo_run( 'ln -s ../sites-available/%s %s'
                              % (self.server_name, self.server_name),
                              password=server.sys_password )


