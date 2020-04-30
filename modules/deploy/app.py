# coding=utf-8

import datetime
import os
from dateutil.relativedelta import relativedelta
from fabric.context_managers import lcd, settings, cd
from fabric.contrib import files
from fabric.contrib.project import rsync_project
from fabric.operations import put, get

from deploy.db_utils import db_exists, drop_db
from deploy_utils import cli_local, PathNotFoundException, cli_run, cli_sudo_run
from git_repo import GitRepo
from gluon.storage import Storage
from m16e import term
from m16e.files import fileutils
from m16e.kommon import is_same_day


def parse_local_init_file( init_file ):
    app_status = Storage()
    for l in init_file.splitlines():
        if l.startswith( '#' ) or len( l.strip() ) == 0:
            continue
        parts = [ p.strip() for p in l.split( '=' ) ]
        if parts[ 0 ] == '__version__':
            app_status.local_version = parts[ 1 ].replace( '"', '' ).replace( "'", "" ).strip()
        elif parts[ 0 ] == '__version_date__':
            app_status.local_version_date = parts[ 1 ].replace( '"', '' ).replace( "'", "" ).strip()
    return app_status


PRESERVE_DIRS = [
    'cache',
    'cron',
    'databases',
    'errors',
    'private',
    # 'static',
    'sessions',
    'uploads' ]

STATIC_LINKS = [
    '403.html',
    '404.html',
    '500.html',
    'css',
    'fonts',
    'images',
    'init_data',
    'js',
    'plugin_timezone' ]

LINK_LIST = [ 'ABOUT',
              'controllers',
              '__init__.py',
              'languages',
              'LICENSE',
              'models',
              'modules',
              'resources',
              'views'
              ]


class AppExistsException( Exception ):
    pass


class App( object ):
    tag = 'app'

    def __init__( self, config ):
        self.config = config
        self.app_name = config.config_data.get( 'app_name' )
        self.master_app_name = self.app_name
        self.app_branch = config.config_data.get( 'app_branch' )
        self.child_prefix = config.config_data.get( 'app_child_prefix' )
        self.cluster = config.get_cluster()
        self.server = config.get_server()
        self.local_folder = config.config_data.get( 'local_folder' ) \
                            % dict( cluster_name=self.cluster.cluster_name )
        self.repo_folder = config.config_data.get( 'app_git_repo' ) \
                           % dict( cluster_name=self.cluster.cluster_name,
                                   app_name=self.app_name )
        self.w3_base_folder = 'sites/%s' % self.cluster.cluster_name
        self.app_status = None
        self.current_release = None
        self.git_repo = None


    def get_git_repo( self ):
        if not self.git_repo:
            self.git_repo = GitRepo( self )
        return self.git_repo


    def get_db_name( self ):
        db_name = self.config.config_data.get( 'app_db_name' ) % dict( cluster_name=self.cluster.cluster_name,
                                                                       app_name=self.app_name )
        return db_name

    def get_abs_local_folder( self, app_name=None ):
        if not app_name:
            app_name = self.master_app_name
        return '%s/web2py/applications/%s' % (self.local_folder,
                                              app_name)


    def get_abs_repo_folder( self, app_name=None ):
        if not app_name:
            app_name = self.app_name
        server = self.server
        return '/'.join( (server.get_sys_home_folder(),
                          self.repo_folder,
                          'apps',
                          app_name))


    def get_abs_w2p_folder( self, app_name=None ):
        if not app_name:
            app_name = self.master_app_name
        return '/'.join( (self.cluster.get_abs_w2p_folder(),
                          'current',
                          'applications',
                          app_name))


    def get_abs_apps_folder( self, app_name=None ):
        if not app_name:
            app_name = self.master_app_name
        return '/'.join( (self.cluster.get_abs_w3_folder(),
                          'apps',
                          app_name) )


    def get_web_app_version( self ):
        server = self.server
        version = version_date = None
        abs_app_folder = self.get_abs_w2p_folder()
        # term.printDebug( 'abs_app_folder: %s' % repr( abs_app_folder ) )
        with settings( host_string=server.get_user_host_string( ),
                       password=server.sys_password ):
            if files.exists( abs_app_folder, use_sudo=True ):
                with cd( abs_app_folder ):
                    ret = cli_run( 'cat __init__.py',
                                   quiet=True )
                    # term.printDebug( 'result: %s' % ret )
                    if ret.stderr:
                        term.printLog( 'ret.stderr: %s' % repr( ret.stderr ) )
                        return ret
                    if ret.startswith( 'abort: ' ):
                        term.printLog( 'result: %s' % ret )
                        return ret

                    if ret.startswith( '/bin/bash: line 0: cd: ' ):
                        term.printLog( 'result: %s' % ret )
                        parts = ret.split( ' ', 5 )
                        msg = 'Path not found: %s' % parts[ 4 ][ : -1 ]
                        raise PathNotFoundException( msg )

                    for l in ret.stdout.splitlines( ):
                        if l.startswith( '#' ) or len( l.strip( ) ) == 0:
                            continue
                        parts = [ p.strip( ) for p in l.split( '=' ) ]
                        if parts[ 0 ] == '__version__':
                            version = parts[ 1 ].replace( '"', '' ).replace( "'", "" ).strip( )
                        elif parts[ 0 ] == '__version_date__':
                            version_date = parts[ 1 ].replace( '"', '' ).replace( "'", "" ).strip( )
            else:
                term.printLog( 'NOT CREATED: %s' % abs_app_folder )
        return (version, version_date)


    def refresh_local_init_version( self ):
        local_path = self.get_abs_local_folder()
        # term.printDebug( 'local_path: %s' % local_path )
        with lcd( local_path ):
            ret = cli_local( 'cat __init__.py', quiet=True )
            if ret.stderr:
                term.printLog( 'ret.stderr: %s' % repr( ret.stderr ) )
                # term.printDebug( 'ret.stderr: %s' % repr( ret.stderr ),
                #                  print_trace=True )

                return ret
            if ret.startswith( 'abort: ' ):
                term.printLog( 'result: %s' % ret )
                return ret

            if ret.startswith( '/bin/bash: line 0: cd: ' ):
                term.printLog( 'result: %s' % ret )
                parts = ret.split( ' ', 5 )
                msg = 'Path not found: %s' % parts[ 4 ][ : -1 ]
                raise PathNotFoundException( msg )

            app_status = parse_local_init_file( ret.stdout )
            return app_status


    def get_app_status( self, refresh=False ):
        if not self.app_status or refresh:
            self.app_status = self.refresh_local_init_version()
            self.app_status.master_app = self.master_app_name
            self.app_status.app_branch = self.app_branch
            git_repo = self.get_git_repo()

            try:
                git_repo.refresh()
                data = { 'v': git_repo.version,
                         'd': git_repo.version_date,
                         'm': self.master_app_name }
                if git_repo.version:
                    msg = '(%(v)s - %(d)s; master: %(m)s)' % data
                    self.app_status.repo_version = git_repo.version
                    self.app_status.repo_version_date = git_repo.version_date
                    self.app_status.repo_msg = msg
                    self.app_status.local_status_resumed = git_repo.local_status_resumed
                    self.app_status.local_status_clean_repo = git_repo.local_status.clean_repo
                    self.app_status.remote_status_resumed = git_repo.remote_status_resumed
                else:
                    msg = '(uninstalled; master: %(m)s)' % data
                    self.app_status.repo_version=None
                    self.app_status.repo_version_date=None
                    self.app_status.repo_msg=msg
                    self.app_status.local_status_resumed = ''
                    self.app_status.remote_status_resumed = ''

            except PathNotFoundException, e:
                term.printLog( 'e: %s' % str( e ) )
                msg = '(%(e)s)' %{ 'e': str( e ) }
                self.app_status.repo_version=None
                self.app_status.repo_version_date=None
                self.app_status.repo_error=e
                self.app_status.repo_msg=msg

            # term.printDebug( 'self.app_status: %s' % repr( self.app_status ), print_trace=True )
            self.app_status.web_version, self.app_status.web_version_date = self.get_web_app_version()
        term.printDebug( 'self.app_status: %s' % repr( self.app_status ) )
        return self.app_status


    def init_remote_repo( self ):
        server = self.server
        with settings( host_string=server.get_user_host_string( ),
                       password=server.sys_password ):
            abs_repo_folder = self.get_abs_repo_folder()
            if files.exists( abs_repo_folder ):
                return ( 'app repo (%s) already exists' % abs_repo_folder,
                         'REPO EXISTS: %s' % abs_repo_folder )

            parent_folder, app_folder = abs_repo_folder.rsplit( '/', 1 )
            cli_run( 'mkdir -p %s' % parent_folder,
                     prompt=True,
                     print_trace=True )
            with cd( parent_folder ):
                cli_run( 'pwd' )
                gr = self.get_git_repo()
                data = dict( app=self.master_app_name,
                             h=gr.git_server,
                             u=gr.git_gitolite_user )
                # data[ 'o' ] = self.cluster.get_git_origin()
                cmd = 'git clone %(u)s@%(h)s:%(app)s' % data
                cli_run( cmd,
                         prompt=True,
                         print_trace=True )


    def checkout_branch( self ):
        server = self.server
        with settings( host_string=server.get_user_host_string() ):
            abs_repo_folder = self.get_abs_repo_folder()
            term.printDebug( 'abs_repo_folder: %s' % repr( abs_repo_folder ) )
            parent_folder, app_folder = abs_repo_folder.rsplit( '/', 1 )
            if not files.exists( parent_folder ):
                return

            with cd( parent_folder ):
                # run( 'pwd' )
                branch = self.app_branch
                if branch:
                    if not files.exists( self.master_app_name ):
                        return

                    with cd( self.master_app_name ):
                        # cli_run( 'pwd' )
                        # with settings( hide( 'stderr', 'warnings' ), warn_only=True ):
                        with settings( warn_only=True ):
                            ret = cli_run( 'git checkout %s' % branch,
                                           quiet=True )


    def init_web_folders( self ):
        server = self.server
        abs_web_folder = self.get_abs_apps_folder()
        release = self.get_current_release()
        cli_sudo_run( 'mkdir -p %s/releases/%s' % (abs_web_folder, release),
                      user=server.w3_user,
                      password=server.sys_password,
                      prompt=True,
                      print_trace=True )
        cli_sudo_run( 'mkdir -p %s/preserve' % (abs_web_folder),
                      user=server.w3_user,
                      password=server.sys_password,
                      prompt=True,
                      print_trace=True )
        with cd( abs_web_folder ):
            with cd( 'preserve' ):
                cli_sudo_run( 'pwd',
                              user=server.w3_user,
                              password=server.sys_password )
                for p in PRESERVE_DIRS:
                    cli_sudo_run( 'mkdir -p %s' % (p),
                                  user=server.w3_user,
                                  password=server.sys_password,
                                  prompt=True,
                                  print_trace=True )


    def get_upload_files_list( self ):
        '''
        Returns:
            config.upload_files_list: [ (<local_file>, <remote_file>), ...]
        '''
        return self.config.config_data.get( 'upload_files_list' )


    def sync_folders( self, upload=True ):
        server = self.server
        folders = self.config.config_data.get( 'sync_folders' )
        local_path = self.get_abs_local_folder( self.app_name )
        remote_path = self.get_abs_w2p_folder( self.app_name )
        with settings( host_string=server.get_user_host_string(),
                       password=server.sys_password ):
            with cd( remote_path ):
                for folder in folders:
                    cli_sudo_run( 'mkdir -p %s' % folder,
                                  password=server.sys_password,
                                  prompt=True,
                                  print_trace=True )
                    with cd( folder ):
                        cli_sudo_run( 'chown -R %s. .' % server.sys_user,
                                      password=server.sys_password,
                                      prompt=True,
                                      print_trace=True )
                    rsync_project( remote_path + '/' + folder + '/',
                                   local_path + '/' + folder + '/',
                                   upload=upload )
                    with cd( folder ):
                        cli_sudo_run( 'chown -R %s. .' % server.w3_user,
                                      password=server.sys_password,
                                      prompt=True,
                                      print_trace=True)


    def put_private_app_file( self, path_tuple ):
        server = self.server
        abs_web_folder = self.get_abs_w2p_folder()
        with settings( host_string=server.get_user_host_string(),
                       password=server.sys_password ):
            app_name = self.master_app_name
            src_path = self.cluster.get_local_folder( app_name )
            dpath = Storage( src=Storage( path=path_tuple[0] ),
                             dest=Storage( path=path_tuple[1] ) )
            if '/' in dpath.src.path:
                dpath.src.folder, dpath.src.filename = dpath.src.path.rsplit( '/', 1 )
            else:
                dpath.src.folder = '.'
                dpath.src.filename = dpath.src.path
            if '/' in dpath.dest.path:
                dpath.dest.folder, dpath.dest.filename = dpath.dest.path.rsplit( '/', 1 )
            else:
                dpath.dest.folder = '.'
                dpath.dest.filename = dpath.dest.path

            src_path += '/web2py/applications/%(app)s/%(f)s' % { 'app': app_name,
                                                                 'f': dpath.src.path }
            put( src_path, 'tmp' )
            tmp_src = '/home/%(user)s/tmp/%(f)s' % { 'user': server.user,
                                                     'f': dpath.src.filename }
            if dpath.dest.folder != '.':
                # term.printDebug( 'dest: %s' % dpath.dest.folder ) #, prompt_continue=True )
                if dpath.dest.folder.startswith( '/' ):
                    abs_dest_path = dpath.dest.folder
                else:
                    abs_dest_path = '%s/current/%s' % (abs_web_folder, dpath.dest.folder)
                # term.printDebug( 'abs_dest_path: %s' % abs_dest_path )
                f_exists = files.exists( abs_dest_path, use_sudo=True ) \
                    or files.is_link( abs_dest_path, use_sudo=True )
                # term.printDebug( 'f_exists: %s' % repr( f_exists ) ) #, prompt_continue=True )
                if not f_exists:
                    cli_sudo_run( 'mkdir -p %s' % abs_dest_path,
                                  user=server.w3_user,
                                  password=server.sys_password,
                                  prompt=True,
                                  print_trace=True )
            if dpath.dest.folder.startswith( '/' ):
                cli_sudo_run( 'cp %s %s' % (tmp_src, dpath.dest.folder),
                              user=server.w3_user,
                              password=server.sys_password,
                              prompt=True,
                              print_trace=True )
            else:
                with cd( abs_web_folder + '/current' ):
                    cli_sudo_run( 'cp %s %s' % (tmp_src, dpath.dest.folder),
                                  user=server.w3_user,
                                  password=server.sys_password,
                                  prompt=True,
                                  print_trace=True )


    def put_private_app_files( self ):
        server = self.server
        app_name = self.master_app_name
        local_folder = self.get_abs_local_folder( app_name=app_name )
        for f in self.get_upload_files_list():
            if '*' in f:
                file_list = cli_local( 'ls -l %s/%s' % (local_folder, f),
                                       prompt=True )
                for fl in file_list:
                    self.put_private_app_file( fl )
            else:
                self.put_private_app_file( f )


    def get_command_list( self ):
        '''
        Returns:
            config.command_list: [ { 'folder': <path>, 'rum': <command>, 'user': <user> }, ...]
        '''
        return self.config.config_data.get( 'command_list' )


    def execute_command_list( self ):
        server = self.server
        abs_apps_folder = self.get_abs_apps_folder()
        with settings( host_string=server.get_user_host_string(),
                       password=server.sys_password ):
            with cd( abs_apps_folder + '/current' ):
                cli_sudo_run( 'pwd',
                              user=server.w3_user,
                              password=server.sys_password )
                for cmd in self.get_command_list():
                    c = Storage( cmd )
                    term.printDebug( 'c: %s' % repr( c ) )
                    with cd( c.folder ):
                        cli_sudo_run( 'pwd',
                                      user=c.user,
                                      password=server.sys_password )
                        cli_sudo_run( c.run,
                                      user=c.user,
                                      password=server.sys_password,
                                      prompt=True,
                                      print_trace=True )


    def config_private_files( self ):
        self.put_private_app_files()
        server = self.server
        with cd( 'private' ):
            cfg_file = 'appconfig.ini'
            theme_name = self.config.app_theme
            if not theme_name:
                term.printLog( 'theme not found', print_trace=True )
            replace_dict = { '{{app_name}}': self.app_name,
                             '{{db_user}}': server.db_user,
                             '{{db_pass}}': server.db_password,
                             '{{db_name}}': self.config.get_db_name( self.app_name ),
                             '{{hostname}}': server.host,
                             '{{mail_server}}': server.mail_server,
                             '{{mail_sender}}': server.mail_sender,
                             '{{mail_login}}': server.mail_login,
                             '{{mail_tls}}': server.mail_tls,
                             '{{meta_name}}': self.cluster.cluster_name,
                             '{{theme_name}}': self.config.theme_name,
                             '{{theme_title}}': self.config.theme_title,
                             '{{theme_subtitle}}': self.config.theme_subtitle,
                             '{{theme_logo_header}}': self.config.theme_logo_header,
                             '{{theme_login_button_position}}': self.config.theme_login_button_position,
                             '{{app_description}}': self.config.app_description,
                             '{{app_keywords}}': self.config.app_keywords,
                             '{{dev_email}}': self.config.dev_email
                             }
            for k in replace_dict:
                cmd = '''sed -i 's/%(k)s/%(v)s/g' %(f)s''' % \
                      { 'k': k,
                        'v': replace_dict[ k ],
                        'f': cfg_file }
                cli_sudo_run( cmd,
                              user=server.w3_user,
                              password=server.sys_password,
                              prompt=True,
                              print_trace=True)


    def install_new_release( self ):
        server = self.server
        abs_repo_folder = self.get_abs_repo_folder()
        abs_apps_folder = self.get_abs_apps_folder()
        # abs_w2p_folder = self.get_abs_w2p_folder()
        release = self.get_current_release()
        with cd( 'releases' ):
            # term.printDebug( 'abs_repo_folder: %s' % repr( abs_repo_folder ) )
            cli_sudo_run( 'mkdir -p %s' % release,
                          password=server.sys_password )
            cli_sudo_run( 'cp -R %s/* %s' % ( abs_repo_folder, release ),
                          password=server.sys_password )
            # term.printDebug( 'abs_web_folder: %s' % repr( abs_web_folder ) )
            cli_sudo_run( 'chown -R %s. %s' % ( server.w3_user, release ),
                          password=server.sys_password )
            # raw_input( 'continue to create links?' )
            with cd( release ):
                for p in PRESERVE_DIRS:
                    cli_sudo_run( 'ln -s %s/preserve/%s %s' % ( abs_apps_folder, p, p ),
                                  user=server.w3_user,
                                  password=server.sys_password,
                                  prompt=True,
                                  print_trace=True)
                cli_sudo_run( 'pwd',
                              user=server.w3_user,
                              password=server.sys_password,
                              prompt=True,
                              print_trace=True )
                # raw_input( 'preserve dirs created, continue?' )
                # term.printDebug( 'release: %s' % release, prompt_continue=True )
                cli_sudo_run( 'cp resources/config/init/appconfig.ini private',
                              user=server.w3_user,
                              password=server.sys_password,
                              prompt=True,
                              print_trace=True )
                cli_sudo_run( 'mkdir -p static/tmp',
                              user=server.w3_user,
                              password=server.sys_password,
                              prompt=True,
                              print_trace=True )
                self.config_private_files()


    def init_web_repo( self ):
        server = self.server
        self.checkout_branch()
        abs_apps_folder = self.get_abs_apps_folder()
        abs_w2p_folder = self.get_abs_w2p_folder()
        # term.printDebug( 'abs_apps_folder: %s' % repr( abs_apps_folder ) )
        # term.printDebug( 'abs_w2p_folder: %s' % repr( abs_w2p_folder ) )
        release = self.get_current_release()
        term.printDebug( 'release: %s' % repr( release ) )
        with settings( host_string=server.get_user_host_string(),
                       password=server.sys_password ):
            self.init_web_folders()
            with cd( abs_apps_folder ):
                self.install_new_release()
                cli_sudo_run( 'ln -s releases/%s current' % release,
                              user=server.w3_user,
                              password=server.sys_password,
                              prompt=True,
                              print_trace=True)
                cli_sudo_run( 'chown -R %s. .' % server.w3_user,
                              password=server.sys_password,
                              prompt=True,
                              print_trace=True)

            w2p_app_folder = '%s/current/applications' % self.cluster.get_abs_w2p_folder()
            with cd( w2p_app_folder ):
                f_link = '%s/current' % ( abs_apps_folder )
                link_name = f_link.rsplit( '/', 2 )[-2]
                if not files.exists( link_name ):
                    cli_sudo_run( 'ln -s %s %s' % ( f_link, link_name ),
                                  user=server.w3_user,
                                  password=server.sys_password )

        self.put_private_app_files()
        self.execute_command_list()


    def update_remote_repo( self ):
        server = self.server
        with settings( host_string=server.get_user_host_string() ):
            abs_repo_folder = self.get_abs_repo_folder()
            if not files.exists( abs_repo_folder ):
                return ( 'app repo does not (%s) exist' % abs_repo_folder,
                         'REPO DOES NOT EXIST: %s' % abs_repo_folder )

            with cd( abs_repo_folder ):
                cmd = 'git pull'
                cli_run( cmd,
                         prompt=True,
                         print_trace=True )
        term.printDebug( 'repo updated' ) #, prompt_continue=True )

    def get_current_release( self ):
        self.get_app_status( refresh=True )
        if not self.current_release:
            self.current_release = '%s-v-%s' % (datetime.datetime.now().strftime( '%Y-%m-%d-%H-%M' ),
                                                self.app_status.repo_version)
        term.printDebug( 'self.app_status: %s' % repr( self.app_status ) )
        term.printDebug( 'self.current_release: %s' % repr( self.current_release ) ) #, print_trace=True, prompt_continue=True )
        return self.current_release


    def upgrade_web_repo( self, compile_jasper=False ):
        server = self.server
        self.checkout_branch()
        # abs_web_folder = self.get_abs_w2p_folder()
        abs_apps_folder = self.get_abs_apps_folder()
        # server.apache_ctl( 'stop' )
        with settings( host_string=server.get_user_host_string(),
                       password=server.sys_password ):
            cli_sudo_run( 'mkdir -p %s/releases/%s' % (abs_apps_folder, self.get_current_release()),
                          user=server.w3_user,
                          password=server.sys_password,
                          prompt=True,
                          print_trace=True )
            with cd( abs_apps_folder ):
                self.install_new_release()
                # self.config_private_files()
                server.apache_ctl( 'stop' )
                cli_sudo_run( 'rm -f current',
                              user=server.w3_user,
                              password=server.sys_password,
                              prompt=True,
                              print_trace=True)
                cli_sudo_run( 'ln -s releases/%s current' % self.get_current_release(),
                              user=server.w3_user,
                              password=server.sys_password,
                              prompt=True,
                              print_trace=True)

        self.put_private_app_files()
        # raw_input( 'private files created, continue?' )
        server.apache_ctl( 'start' )
        self.execute_command_list()


    def purge_web_folder( self ):
        server = self.server
        cluster = self.cluster
        w2p_folder = cluster.get_abs_w2p_folder()
        with settings( host_string=server.get_user_host_string(),
                       password=server.sys_password ):
            w2p_folder = '%s/current/applications' % w2p_folder
            with cd( w2p_folder ):
                if files.exists( self.app_name ):
                    raw_input( 'delete %s in %s' % (self.app_name, w2p_folder) )
                    cli_sudo_run( 'rm -f %s' % ( self.app_name ),
                                  user=server.w3_user,
                                  password=server.sys_password,
                                  prompt=True,
                                  print_trace=True )
            apps_folder = cluster.get_abs_w3_folder() + '/apps/' + self.master_app_name
            cli_sudo_run( 'rm -rf %s' % apps_folder,
                          user=server.w3_user,
                          password=server.sys_password,
                          prompt=True,
                          print_trace=True )


    def purge_remote_repo( self ):
        server = self.server
        with settings( host_string=server.get_user_host_string() ):
            abs_repo_folder = self.get_abs_repo_folder()
            # term.printDebug( 'purging folder: %s' % abs_repo_folder )
            cli_run( 'rm -rf %s' % abs_repo_folder,
                     prompt=True,
                     print_trace=True )


    def list_error_files( self, age ):
        # term.printDebug( 'age: %s' % age )
        abs_apps_folder = self.get_abs_apps_folder()
        # term.printDebug( 'abs_apps_folder: %s' % abs_apps_folder )
        server = self.server
        with settings( host_string=server.get_user_host_string(),
                       password=server.sys_password ):
            path = abs_apps_folder + '/preserve/errors/'
            if age == '*':
                cmd = 'find -L %(path)s -type f' % dict( path=path )
            else:
                cmd = 'find -L %(path)s -mtime +%(age)s -type f' % dict( path=path, age=age )
            # term.printDebug( 'cmd: %s' % cmd )
            lst = cli_sudo_run( cmd,
                                user=server.w3_user,
                                password=server.sys_password )
            # term.printDebug( 'lst: %s' % lst ) #, prompt_continue=True )
            return lst.splitlines()


    def delete_error_files( self, age ):
        # term.printDebug( 'age: %s' % age )
        abs_apps_folder = self.get_abs_apps_folder()
        # term.printDebug( 'abs_apps_folder: %s' % abs_apps_folder )
        server = self.server
        with settings( host_string=server.get_user_host_string(),
                       password=server.sys_password ):
            path = abs_apps_folder + '/preserve/errors/'
            cmd = 'find -L %(path)s -mindepth 1 -mtime +%(age)s -type f -delete' % dict( path=path, age=age )
            cli_sudo_run( cmd,
                          user=server.w3_user,
                          password=server.sys_password,
                          quiet=True )
            # term.printDebug( 'lst: %s' % lst, prompt_continue=True )
            children = self.get_child_list()
            for c in children:
                abs_apps_folder = self.get_abs_apps_folder( app_name=c )
                path = abs_apps_folder + '/preserve/errors/'
                cmd = 'find -L %(path)s -mindepth 1 -mtime +%(age)s -type f -delete' % dict( path=path, age=age )
                cli_sudo_run( cmd,
                              user=server.w3_user,
                              password=server.sys_password )


    def remove_sessions( self ):
        abs_w2p_folder = self.cluster.get_abs_w2p_folder() + '/current'
        server = self.server
        with settings( host_string=server.get_user_host_string(),
                       password=server.sys_password ):
            with cd( abs_w2p_folder ):
                cmd = 'python web2py.py -S %s -M -R scripts/sessions2trash.py' % self.app_name
                cli_sudo_run( cmd,
                              user=server.w3_user,
                              password=server.sys_password )
                children = self.get_child_list()
                for c in children:
                    cmd = 'python web2py.py -S %s -M -R scripts/sessions2trash.py' % c
                    cli_sudo_run( cmd,
                                  user=server.w3_user,
                                  password=server.sys_password )


    def list_releases( self ):
        abs_apps_folder = self.get_abs_apps_folder()
        # term.printDebug( 'abs_web_cluster_base_folder: %s' % abs_web_cluster_base_folder )
        server = self.server
        release_list = Storage()
        with settings( host_string=server.get_user_host_string(),
                       password=server.sys_password ):
            with cd( abs_apps_folder):
                if files.exists( 'releases' ):
                    with cd( 'releases' ):
                        rel_list = cli_sudo_run( 'ls -t',
                                                 user=server.w3_user,
                                                 password=server.sys_password,
                                                 quiet=True ).split()
                        # term.printDebug( 'rel_list: %s' % rel_list )
                        for rel in rel_list:
                            print( 'rel: [%s]' % rel )
                            r_date = rel[  : 16 ]
                            # term.printDebug( 'r_date: %s' % r_date )
                            f_date = datetime.datetime.strptime( r_date, '%Y-%m-%d-%H-%M' )
                            release_list[ rel ] = Storage( f_date=f_date )

        return release_list


    def remove_old_releases( self, rel_list, prompt_user=False ):
        abs_apps_folder = self.get_abs_apps_folder()
        # term.printDebug( 'abs_apps_folder: %s' % abs_apps_folder )
        rel_list = sorted( rel_list )
        # term.printDebug( 'rel_list: %s' % repr( rel_list ) )
        # raw_input( 'continue?' )
        server = self.server

        with settings( host_string=server.get_user_host_string(),
                       password=server.sys_password ):
            with cd( abs_apps_folder + '/releases' ):
                ret = cli_sudo_run( 'pwd',
                                    user=server.w3_user,
                                    password=server.sys_password )
                for rel_name in rel_list:
                    if prompt_user:
                        # term.printDebug( 'remove RELEASE %s/%s?' % (ret, rel_name) )
                        if raw_input( 'continue [Silent]?' ) == 'S':
                            prompt_user = False
                    cli_sudo_run( 'rm -rf %s' % rel_name,
                                  user=server.w3_user,
                                  password=server.sys_password )


    def clear_old_releases( self, age=5, preserve=3 ):
        rel_list = self.list_releases()
        # term.printDebug( 'rel_list: %s' % repr( rel_list ) )

        # build preserve list
        pf_list = []
        idx = 0
        last_day = None
        for r in sorted( rel_list.keys(), reverse=True ):
            rel = rel_list[ r ]
            rel.idx = idx
            # term.printDebug( 'rel_list[ "%s" ]: %s' % ( r, repr( rel_list[ r ] ) ) )
            # term.printDebug( 'last_day: %s; f_date: %s' % ( repr( last_day ), repr( rel.f_date ) ) )
            same_day = last_day and is_same_day( last_day, rel.f_date )
            # term.printDebug( 'same_day: %s' % repr( same_day) )
            if not same_day:
                d_dif = relativedelta( datetime.date.today( ), rel.f_date )
                # term.printDebug( 'd_dif: %s' % repr( d_dif ) )
                if d_dif.years == 0 and d_dif.months == 0 and d_dif.days <= age:
                    pf_list.append( r )
                    # term.printDebug( 'BLUE: %2d - %s' % (idx, r) )
            idx += 1
            last_day = rel.f_date

        # term.printDebug( 'pf_list: %s' % repr( pf_list ) )
        # build remove list
        of_list = []
        idx = 0
        last_day = None
        for r in sorted( rel_list.keys(), reverse=True ):
            rel = rel_list[ r ]
            # term.printDebug( 'last_day: %s; f_date: %s' % ( repr( last_day ), repr( rel.f_date ) ) )
            same_day = last_day and is_same_day( last_day, rel.f_date )
            # term.printDebug( 'same_day: %s' % repr( same_day) )
            if same_day:
                of_list.append( r )
                # term.printDebug( '--- RED:  %2d - %s' % ( idx, r ) )
            elif len( pf_list ) < preserve:
                # term.printDebug( '+++ BLUE:  %2d - %s' % (idx, r) )
                if not r in pf_list:
                    # term.printDebug( '+++ BLUE:  %2d - %s' % (idx, r) )
                    pf_list.append( r )
            elif r not in pf_list:
                of_list.append( r )
                # term.printDebug( '--- RED:  %2d - %s' % ( idx, r ) )
            idx += 1
            last_day = rel.f_date

        # term.printDebug( 'of_list: %s' % repr( of_list ) )
        # term.printDebug( 'pf_list: %s' % repr( pf_list ) )
        print( term.fg_blue( 'KEEP:' ) )
        for r in sorted( pf_list, reverse=True ):
            # term.printDebug( 'rel_list[ %s ]: %s' % (r, rel_list[ r ] ) )
            print( term.fg_blue( '%2d - %s' % ( rel_list[ r ].idx, r ) ) )
        print( term.fg_red( 'DELETE:' ) )
        for r in sorted( of_list, reverse=True ):
            print( term.fg_red( '%2d - %s' % ( rel_list[ r ].idx, r ) ) )
        self.remove_old_releases( of_list )


    def upgrade_app( self, v_from, v_to ):
        server = self.server
        cluster = self.cluster
        w2p_folder = cluster.get_abs_w2p_folder()
        with settings( host_string=server.get_user_host_string(),
                       password=server.sys_password ):
            w2p_folder = '%s/current' % w2p_folder
            with cd( w2p_folder ):
                cmd = 'nice python web2py.py ' \
                      '-i 127.0.0.1 -M ' \
                      '-S %(a)s -R ' \
                      'applications/%(a)s/resources/upgrades/%(t)s' \
                      '/upd_FROM_%(f)s.py' % { 'a': self.app_name,
                                               'f': v_from,
                                               't': v_to }
                # term.printDebug( 'cmd: %s' % cmd )
                # raw_input( 'continue?' )
                cli_sudo_run( cmd,
                              user=server.w3_user,
                              password=server.sys_password,
                              prompt=True )
                for c in self.get_child_list():
                    cmd = 'nice python web2py.py ' \
                          '-i 127.0.0.1 -M ' \
                          '-S %(a)s -R ' \
                          'applications/%(a)s/resources/upgrades/%(t)s' \
                          '/upd_FROM_%(f)s.py' % { 'a': c,
                                                   'f': v_from,
                                                   't': v_to }
                    # term.printDebug( 'cmd: %s' % cmd )
                    # raw_input( 'continue?' )
                    ret = cli_sudo_run( cmd,
                                        user=server.w3_user,
                                        password=server.sys_password,
                                        prompt=True )
                    if 'Traceback' in str( ret ):
                        cont = raw_input( 'continue?' )
                        if cont.lower().startswith( 'n' ):
                            break


    def get_child_list( self ):
        server = self.server
        cluster = self.cluster
        w2p_folder = cluster.get_abs_w2p_folder()
        app_list = []
        if self.child_prefix:
            with settings( host_string=server.get_user_host_string(),
                           password=server.sys_password ):
                with cd( '%s/current/applications' % w2p_folder ):
                    ret = cli_sudo_run( 'ls',
                                        user=server.w3_user,
                                        password=server.sys_password,
                                        prompt=True,
                                        print_trace=True )
                    term.printDebug( 'ret: %s' % repr( ret ) )
                    a = ret.split()
                    term.printDebug( 'a: %s' % repr( a ) )
                    for f in a:
                        if f.startswith( self.child_prefix ):
                            app_list.append( f )
        return app_list


    def app_exists( self, app_name ):
        server = self.server
        folder = self.get_abs_w2p_folder( app_name=app_name )
        term.printDebug( 'folder: %s' % folder )
        with settings( host_string=server.get_user_host_string(),
                       password=server.sys_password ):
            res = files.exists( folder,
                                use_sudo=True )
        return res



    def get_appconfig( self, app_name ):
        server = self.server
        abs_app_folder = self.get_abs_local_folder( app_name )
        term.printDebug( 'abs_app_folder: %s' % repr( abs_app_folder ) )
        # blm_folder = abs_app_folder + '/' + version
        # blm_folder = APPS_FOLDER + '/belmiro/%s' % version
        blm_ac_file = abs_app_folder + '/resources/config/init/appconfig.ini'
        ac = fileutils.read_file( os.path.expanduser( blm_ac_file ) )
        db_name = self.config.get_db_name( app_name )
        ac = ac.replace( '{{db_name}}', db_name )
        ac = ac.replace( '{{db_user}}', server.db_user )
        ac = ac.replace( '{{db_pass}}', server.db_password )
        ac = ac.replace( '{{mail_server}}', server.mail_server )
        ac = ac.replace( '{{mail_sender}}', server.mail_sender )
        ac = ac.replace( '{{mail_login}}', server.mail_login )
        ac = ac.replace( '{{mail_tls}}', server.mail_tls )
        ac = ac.replace( '{{dev_email}}', server.dev_email )
        return ac


    def init_child_app( self, child_name ):
        '''
        \-+-- current_app_folder
            +-- preserve
            | +-- cache
            | +-- (...)
            | +-- uploads
            +-- current
              +-- _master_app -> .../belmiro/current
              +-- _preserve -> ../../preserve

              +-- ABOUT -> _master_app/ABOUT
              +-- controllers -> _master_app/controllers
              +-- __init__.py -> _master_app/__init__.py
              +-- languages -> _master_app/languages
              +-- LICENSE -> _master_app/LICENSE
              +-- models -> _master_app/models
              +-- modules -> _master_app/modules
              +-- private -> _master_app/private
              +-- views -> _master_app/views

              +-- cache -> _preserve/cache
              +-- cron -> _preserve/cron
              +-- databases -> _preserve/databases
              +-- errors -> _preserve/errors
              +-- sessions -> _preserve/sessions
              +-- static -> _master_app/static
              +-- static/* -> _preserve/static/*
              +-- uploads -> _preserve/uploads

        '''
        if self.app_exists( child_name ):
            raise AppExistsException( 'App (%s) already exists' % child_name )

        abs_app_folder = self.get_abs_apps_folder()

        aaf_path = abs_app_folder.rsplit( '/', 1 )

        app_folder = aaf_path[ 0 ] + '/' + child_name

        blm_folder = abs_app_folder + '/current'

        server = self.server
        self.checkout_branch()

        term.printDebug( 'abs_app_folder: %s' % abs_app_folder )
        term.printDebug( 'app_folder: %s' % app_folder )
        # STATIC_LINKS = [
        #     '403.html',
        #     '404.html',
        #     '500.html',
        #     'css',
        #     'fonts',
        #     'images',
        #     'init_data',
        #     'js',
        #     'plugin_timezone' ]
        #
        # LINK_LIST = [ 'ABOUT',
        #               'controllers',
        #               '__init__.py',
        #               'languages',
        #               'LICENSE',
        #               'models',
        #               'modules',
        #               'static/*',
        #               'views'
        #               ]
        d_list = PRESERVE_DIRS
        m_list = LINK_LIST
            # ('ABOUT', 'controllers', '__init__.py', 'languages',
            #       'LICENSE', 'models', 'modules',
            #       'resources', 'static', 'views')
        with settings( host_string=server.get_user_host_string(),
                       password=server.sys_password ):
            if files.exists( app_folder,
                             use_sudo=True ):
                raise Exception( 'App folder (%s) already exists' % app_folder )
            cli_sudo_run( 'mkdir -p ' + app_folder,
                          user=server.w3_user,
                          password=server.sys_password,
                          prompt=True,
                          print_trace=True )
            with cd( app_folder ):
                for d in d_list:
                    cli_sudo_run( 'mkdir -p preserve/' + d,
                                  user=server.w3_user,
                                  password=server.sys_password,
                                  prompt=True )
                cli_sudo_run( 'mkdir -p preserve/static',
                              user=server.w3_user,
                              password=server.sys_password,
                              prompt=True )
                cli_sudo_run( 'mkdir -p current',
                              user=server.w3_user,
                              password=server.sys_password,
                              prompt=True )
                with cd( 'current' ):
                    # local( 'ln -s %s _master_app' % blm_folder )
                    cli_sudo_run( 'ln -s %s _master_app' % blm_folder,
                                  user=server.w3_user,
                                  password=server.sys_password,
                                  prompt=True )
                    # local( 'ln -s ../preserve _preserve' )
                    cli_sudo_run( 'ln -s ../preserve _preserve',
                                  user=server.w3_user,
                                  password=server.sys_password,
                                  prompt=True )
                    for d in d_list:
                        # local( 'ln -s _preserve/%(d)s %(d)s' % { 'd': d } )
                        cli_sudo_run( 'ln -s _preserve/%(d)s %(d)s' % { 'd': d },
                                      user=server.w3_user,
                                      password=server.sys_password,
                                      prompt=True )
                    cli_sudo_run( 'ln -s _preserve/static static',
                                  user=server.w3_user,
                                  password=server.sys_password,
                                  prompt=True )
                    for m in m_list:
                        # local( 'ln -s _master_app/%(m)s %(m)s' % { 'm': m } )
                        cli_sudo_run( 'ln -s _master_app/%(m)s %(m)s' % { 'm': m },
                                      user=server.w3_user,
                                      password=server.sys_password,
                                      prompt=True )
                    with cd( 'static' ):
                        for f in STATIC_LINKS:
                            cli_sudo_run( 'ln -s ../../current/_master_app/static/%(f)s %(f)s' % { 'f': f },
                                          user=server.w3_user,
                                          password=server.sys_password,
                                          prompt=True )

                    ac = self.get_appconfig( self.master_app_name )
                    filename = fileutils.write_tmp_file( ac )
                    put( filename, '~/tmp' )
                    cfg_file = '%s/current/private/appconfig.ini' % app_folder
                    cli_sudo_run( 'mv %(uh)s%(f)s %(af)s' %
                                  { 'uh': '/home/' + server.sys_user,
                                    'f': filename,
                                    'af': cfg_file },
                                  password=server.sys_password,
                                  prompt=True )
                    cli_sudo_run( 'chown -R %s. .' % server.w3_user,
                                  password=server.sys_password,
                                  prompt=True )

                    with cd( 'private' ):
                        cli_sudo_run( 'ln -s %s/private/keys keys' % blm_folder,
                                      user=server.w3_user,
                                      password=server.sys_password,
                                      prompt=True )
            term.printDebug( 'app_name: %s' % self.app_name )
            term.printDebug( 'child_name: %s' % child_name )
            w2p_folder = self.cluster.get_abs_w2p_folder()
            with cd( w2p_folder + '/current' ):
                with cd( 'applications' ):
                    cli_sudo_run( 'ln -s %(f)s/current %(n)s' %
                                  { 'f': app_folder,
                                    'n': child_name } )
                    # with cd( child_name ):
                    #     cli_sudo_run( 'touch TESTING' )


    def purge_child_app( self, child_name ):
        '''
        '''
        # if not self.app_exists( child_name ):
        #     raise Exception( 'App (%s) does NOT exist' % child_name )

        abs_app_folder = self.get_abs_app_web_folder( app_name=child_name )
        srv_ctx = self.srv_ctx
        server = srv_ctx.server
        term.printDebug( 'abs_app_folder: %s' % abs_app_folder )
        with settings( host_string=server.get_user_host_string(),
                       password=server.sys_password ):
            if self.web_app_exists( child_name ):
                w2p_folder = self.get_abs_w2p_web_folder()
                with cd( w2p_folder + '/current' ):
                    with cd( 'applications' ):
                        cli_sudo_run( 'rm -f %(n)s' % { 'n': child_name } )

            if self.app_exists( child_name ):
                cli_sudo_run( 'rm -rf ' + abs_app_folder,
                              user=server.w3_user,
                              password=server.sys_password,
                              prompt=True,
                              print_trace=True )


    def pull_db( self, compression='j' ):
        server = self.server
        db_name = self.get_db_name()
        remote_folder = 'tmp/downloads'
        local_folder = '~/tmp/downloads'
        if compression == 'z':
            ext = 'tgz'
        else:
            ext = 'bz2'
        d = { 'db_name': db_name,
              'compression': compression,
              'ext': ext }
        sql_filename = 'dump-%(db_name)s.sql' % d
        with settings( host_string=server.get_user_host_string(),
                       password=server.sys_password ):
            cli_run( 'mkdir -p %s' % remote_folder )
            d[ 'f' ] = sql_filename
            d[ 'l' ] = local_folder
            with cd( remote_folder ):
                cli_run( 'pg_dump -C %(db_name)s -f %(f)s' % d )
                cli_run( 'tar %(compression)scvf %(f)s.tar.%(ext)s %(f)s' % d )
                get( '%(f)s.tar.%(ext)s' %d,
                     '%(l)s/%(f)s.tar.%(ext)s' % d )
                with lcd( local_folder ):
                    cli_local( 'tar %(compression)sxvf %(f)s.tar.%(ext)s %(f)s' % d )
                    with settings( warn_only = True ):
                        cli_local( 'dropdb %s' % db_name )
                    cli_local( 'psql -f %(f)s -v ON_ERROR_STOP=1' % d )
        # self.sync_folders( upload=False )


    def push_db( self, compression='j' ):
        server = self.server
        db_name = self.get_db_name()
        folder = '~/tmp/downloads'
        sql_filename = 'dump-%s.sql' % db_name
        cli_local( 'mkdir -p %s' % folder )
        if compression == 'z':
            ext = 'tgz'
        else:
            ext = 'bz2'
        with lcd( folder ):
            tarball = '%s.tar.%s' % (sql_filename, ext)
            cli_local( 'pg_dump -C %s -f %s' % (db_name, sql_filename) )
            cli_local( 'tar %scvf %s %s' % (compression, tarball, sql_filename) )

        with settings( host_string=server.get_user_host_string(),
                       password=server.sys_password ):
            cli_run( 'mkdir -p tmp' )
            tarball = '%s.tar.%s' % (sql_filename, ext)
            put( '%s/%s' % (folder, tarball),
                 'tmp/%s' % tarball )
            with cd( 'tmp' ):
                filename = cli_run( 'tar %sxvfm %s' % (compression, tarball) )
                # term.printDebug( 'filename: %s' % filename )
                cli_run( 'ls -l %s' % filename )

                cmd = '''sed -i 's/SET lock_timeout/-- SET lock_timeout/g
                                 s/SET idle_in_transaction_session_timeout/-- SET idle_in_transaction_session_timeout/g
                                 s/SET row_security/-- SET row_security/g' %s''' % filename
                # term.printDebug( 'cmd: %s' % (cmd % filename) )
                cli_run( cmd )

                cmd = '''sed -i 's/OWNER TO carlos/OWNER TO %s/g' %s'''
                cli_run( cmd % (server.db_user, filename) )

                cmd = '''sed -i 's/Owner: carlos/Owner: %s/g' %s'''
                cli_run( cmd % (server.db_user, filename) )

                if db_exists( server, db_name ):
                    drop_db(  server, db_name )
                cli_run( 'psql -f %s -v ON_ERROR_STOP=1' % filename )
            # self.sync_folders( upload=True )


    def get_app_i18n_files( self ):
        server = self.server
        remote_folder = '%s/tmp/downloads' % server.get_sys_home_folder()
        local_folder = '~/tmp/downloads'
        abs_app_folder = self.get_abs_w2p_folder()
        ext = 'bz2'
        d = { 'compression': 'j',
              'ext': ext,
              'app_name': self.master_app_name,
              'cluster_name': self.cluster.cluster_name }
        i18n_filename = 'dump-%(cluster_name)s-%(app_name)s-i18n.%(ext)s' % d
        d[ 'f' ] = i18n_filename
        with settings( host_string=server.get_user_host_string(),
                       password=server.sys_password ):
            cli_run( 'mkdir -p %s' % remote_folder )
            with cd( abs_app_folder ):
                d[ 'tmp' ] = remote_folder
                cmd = 'tar jcvf %(tmp)s/%(f)s languages/*' % d
                cli_sudo_run( cmd,
                              # user=server.w3_user,
                              password=server.sys_password,
                              prompt=True,
                              print_trace=True )
                cli_sudo_run( 'chown -R %s. %s' % (server.sys_user, remote_folder),
                              # user=server.w3_user,
                              password=server.sys_password,
                              prompt=True,
                              print_trace=True )
            with lcd( local_folder ):
                cli_local( 'pwd' )
                src = '%(tmp)s/%(f)s' %d
                dest = '%(f)s' % d
                get( src, dest )
                cli_local( 'rm -rf languages' )
                cli_local( 'tar %(compression)sxvf %(f)s' % d )
        # self.sync_folders( upload=False )


