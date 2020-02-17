#! /usr/bin/python
# coding=utf-8

from fabric.context_managers import lcd, cd, settings
from datetime import timedelta
from fabric.contrib import files

from deploy_utils import cli_run, PathNotFoundException, cli_local
from gluon.storage import Storage
from m16e import term
from m16e.kommon import DT
from m16e.text.text import get_padded_str
from vcs_repo import VcsRepo


class GitRepo( VcsRepo ):

    def __init__( self, current_app ):
        super( GitRepo, self ).__init__( current_app )
        cfg = current_app.config
        self.git_server = cfg.config_data.get( 'git_server' )
        self.git_user_name = cfg.config_data.get( 'git_user_name' )
        self.git_user_email = cfg.config_data.get( 'git_user_email' )
        self.git_gitolite_user = cfg.config_data.get( 'git_gitolite_user' )
        self.git_origin = cfg.config_data.get( 'git_origin' )


    def __repr__( self ):
        s = ''
        s += 'version: %s\n' % (repr( self.version ) )
        s += 'version_date: %s\n' % (repr( self.version_date ) )
        s += 'changeset.status_branch: %s\n' % (repr( self.get_status_branch() ) )
        s += 'changeset.status_clean: %s\n' % (repr( self.is_repo_clean() ) )
        s += ' ---\nerrors: %s\n' % (repr( self.errors ) )
        return s


    def __str__(self, *args, **kwargs):
        data = { 'ver': self.version or '',
                 'ver_date': self.version_date or '',
                 'st_branch': self.get_status_branch(),
                 'is_clean': self.is_repo_clean(),
                 'changeset': self.get_changeset_id(),
                 'author': self.get_author() }
        data[ 'date' ] = '-'
        if self.version_date:
            data[ 'date' ] = self.version_date

        s = '''version: %(ver)s; date: %(date)s; status: %(is_clean)s [branch: %(st_branch)s]; ''' \
            '''changeset: %(changeset)s; author: %(author)s''' % data
        return s


    def parse_timestamp( self, value, mask=None ):
        d = None
        h_adjust = -1   # server time in TZ Europe/Lisbon
        m_adjust = 0
        if value:
            if value[ -5 ] in '+-':
                s = value[ -5 : ]
                h_adjust += int( s[ 1 : 3 ] )
                m_adjust += int( s[ 3 : ] )
                value = value[ : -5 ].strip()
            if mask:
                masks = [ mask ]
            else:
                masks = [ '%a %b %d %H:%M %Y',
                          '%Y-%m-%d %H:%M:%S.%f',
                          '%Y-%m-%d %H:%M:%S',
                          '%Y-%m-%d %H:%M' ]
            for mask in masks:
                try:
                    d = DT.strptime( value, mask )
                    d += timedelta( hours=h_adjust,
                                    minutes=m_adjust )
                    break
                except ValueError:
                    pass
        return d


    # line format (LF_) lengths
    LF_VER_LEN = 12
    LF_DATE_LEN = 14
    LF_STATUS_LEN = 20
    LF_CHANGESET_LEN = 16


    def get_format_status_header( self, style='line' ):
        l = get_padded_str( 'Version', self.LF_VER_LEN )
        l += ' ' + get_padded_str( 'Date', self.LF_DATE_LEN )
        l += ' ' + get_padded_str( 'Status', self.LF_STATUS_LEN )
        l += ' ' + get_padded_str( 'Changeset', self.LF_CHANGESET_LEN )
#         term.printDebug( 'l: [%s]' % repr( l ) )
        return l


    def format_status( self, style='line' ):
        # term.printDebug( 'self: %s' % repr( self ) )
        v = self.version or ''
        # term.printDebug( 'v: [%s]' % repr( v ) )
        l = get_padded_str( v, self.LF_VER_LEN )
        # term.printDebug( 'l: [%s]' % repr( l ) )

        v = self.version_date or ''
        # term.printDebug( 'v: [%s]' % repr( v ) )
        l += ' ' + get_padded_str( v, self.LF_DATE_LEN )
        # term.printDebug( 'l: [%s]' % repr( l ) )

        v = 'Clean' if self.is_repo_clean() else 'Changed'
        # term.printDebug( 'v: [%s]' % repr( v ) )
        l += ' ' + get_padded_str( v, self.LF_STATUS_LEN )
        # term.printDebug( 'l: [%s]' % repr( l ) )

        v = self.get_changeset_id()
        # term.printDebug( 'v: [%s]' % repr( v ) )
        l += ' ' + get_padded_str( v, self.LF_CHANGESET_LEN )
        # term.printDebug( 'l: [%s]' % repr( l ) )
        return l


    def parse_init_file( self, init_file ):
        for l in init_file.splitlines():
            if l.startswith( '#' ) or len( l.strip() ) == 0:
                continue
            parts = [ p.strip() for p in l.split( '=' ) ]
            if parts[0] == '__version__':
                self.version = parts[1].replace( '"', '' ).replace( "'", "" ).strip()
            elif parts[0] == '__version_date__':
                self.version_date = parts[1].replace( '"', '' ).replace( "'", "" ).strip()


    def refresh_init_version( self ):
        config = self.current_app.config
        server = config.get_server()
        abs_app_folder = self.current_app.get_abs_repo_folder()
        # term.printDebug( 'abs_app_folder: %s' % repr( abs_app_folder ) ) #, prompt_continue=True )
        # with settings( host_string=server.get_user_host_string(),
        #                password=server.sys_password,
        #                hide='output' ):
        with settings( host_string=server.get_user_host_string(),
                       password=server.sys_password ):
            cli_run( 'cat /etc/hostname' )
            cli_run( 'pwd' )
            if files.exists( abs_app_folder ):
                with cd( abs_app_folder ):
                    cli_run( 'pwd' )
                    ret = cli_run( 'cat __init__.py',
                                   quiet=True )
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

                    self.parse_init_file( ret.stdout )
            else:
                self.version = 'none'
                self.version_date = 'none'


    # def parse_status( self, status_str ):
    #     term.printDebug( 'status_str: [%s]' % status_str )
    #     lines = status_str.splitlines()
    #     if len( lines ) > 1:
    #         status = Storage( branch=lines[0][ 10 : ],
    #                           clean_repo=lines[1].startswith( 'nothing to commit,' ) )
    #     else:
    #         status = Storage( branch='None',
    #                           clean_repo=False )
    #
    #     # term.printDebug( 'self.status: %s' % repr( self.status ) )
    #     return status
    #
    #
    def refresh_local_status( self ):
        app = self.current_app
        local_folder= app.get_abs_local_folder()
        with lcd( local_folder ):
            # term.printDebug( 'local_folder: %s' % local_folder )
            result = cli_local( 'git status',
                                quiet=True )
            if result.stderr:
                term.printLog( 'result.stderr: %s' % repr( result.stderr ) )
                return result
            if result.startswith( 'abort: ' ):
                term.printLog( 'result: %s' % repr( result ) )
                return result

            # term.printDebug( 'result.stdout: %s' % repr( result.stdout ) )
            # term.printDebug( 'result.stderr: %s' % repr( result.stderr ) )
            lines = result.stdout.splitlines()
            if len( lines ) > 1:
                self.local_status = Storage( branch=lines[ 0 ][ 10: ],
                                             clean_repo=lines[ 1 ].startswith( 'nothing to commit,' ) )
            else:
                self.local_status = Storage( branch='None',
                                             clean_repo=False )

            if self.local_status.clean_repo:
                self.local_status_resumed = term.fg_green( '(nothing to commit)' )
            else:
                self.local_status_resumed = '%s\n%s' % (term.fg_red( '(uncommited files)' ),
                                                        term.fg_red( result.stdout ) )


    def refresh_remote_status( self ):
        config = self.current_app.config
        server = config.get_server()
        cluster = config.get_cluster()
        abs_app_folder = self.current_app.get_abs_repo_folder()
        # term.printDebug( 'abs_app_folder: %s' % repr( abs_app_folder ) ) #, prompt_continue=True )
        with settings( host_string=server.get_user_host_string(),
                       password=server.sys_password,
                       hide='output' ):
            if files.exists( abs_app_folder ):
                with cd( abs_app_folder ):
                    result = cli_run( 'git status',
                                      quiet=True )
                    if result.stderr:
                        term.printLog( 'result.stderr: %s' % repr( result.stderr ) )
                        return result
                    if result.startswith( 'abort: ' ):
                        term.printLog( 'result: %s' % repr( result ) )
                        return result

                    # term.printDebug( 'result.stdout: %s' % repr( result.stdout ) )
                    # term.printDebug( 'result.stderr: %s' % repr( result.stderr ) )
                    lines = result.stdout.splitlines()
                    if len( lines ) > 1:
                        self.remote_status = Storage( branch=lines[ 0 ][ 10: ],
                                                      clean_repo=lines[ 1 ].startswith( 'Your branch is up-to-date with ' ) )
                    else:
                        self.remote_status = Storage( branch='None',
                                                      clean_repo=False )
                    if self.remote_status.clean_repo:
                        self.remote_status_resumed = term.fg_green( '(nothing to commit)' )
                    else:
                        self.remote_status_resumed = '%s\n%s' % (term.fg_red( '(uncommited files)' ),
                                                                 term.fg_red( result.stdout ) )
            else:
                self.remote_status_resumed = term.fg_red( '(no repo)' )
                self.remote_status = Storage( branch='None',
                                              clean_repo=False )


    def parse_changeset( self, changeset_output ):
        self.changeset = Storage()
        lines = changeset_output.splitlines()
        i = 0
        l = lines[ i ]
        self.changeset.id = l[ 7 : ]
        i += 1
        self.changeset.author = l[ 8 : ]
        i += 1
        self.changeset.timestamp = self.parse_timestamp( l[ 8 : ] )
        self.changeset.commit_msg = ' '.join( lines[ i : ] ).strip()


    def refresh_changeset( self ):
        config = self.current_app.config
        server = config.get_server()
        cluster = config.get_cluster()
        abs_app_folder = self.current_app.get_abs_repo_folder()
        # term.printDebug( 'abs_app_folder: %s' % repr( abs_app_folder ) )
        with settings( host_string=server.get_user_host_string(),
                       password=server.sys_password,
                       hide='output' ):
            with cd( abs_app_folder ):
                result = cli_run( 'git log -1',
                                  quiet=True )
                if result.stderr:
                    term.printLog( 'result.stderr: %s' % repr( result.stderr ) )
                    return result
                if result.startswith( 'abort: ' ):
                    term.printLog( 'result: %s' % result )
                    return result

                self.parse_changeset( result.stdout )


    def checkout_branch( self ):
        config = self.current_app.config
        server = config.get_server()
        cluster = config.get_cluster()
        app = config.get_app()
        with settings( host_string=server.get_user_host_string() ):
            abs_repo_folder = app.get_abs_repo_folder( self.current_app.master_app_name )
            # term.printDebug( 'abs_repo_folder: %s' % repr( abs_repo_folder ) )
            parent_folder, app_folder = abs_repo_folder.rsplit( '/', 1 )
            if not files.exists( parent_folder ):
                return

            with cd( parent_folder ):
                # run( 'pwd' )
                # data = dict( app=self.current_app.app_name,
                #              h=server.name,
                #              u=server.git.gitolite_user )
                # data[ 'o' ] = cluster.get_git_origin()
                # if data[ 'o' ] != 'origin':
                #     cmd = 'git clone --origin %(o)s %(u)s@%(h)s:%(app)s' % data
                # else:
                branch = app.app_branch
                if branch:
                    if not files.exists( self.current_app.master_app_name ):
                        return

                    with cd( self.current_app.master_app_name ):
                        # cli_run( 'pwd' )
                        # with settings( hide( 'stderr', 'warnings' ), warn_only=True ):
                        with settings( warn_only=True ):
                            ret = cli_run( 'git checkout %s' % branch,
                                           quiet=True )
                            # ret = cli_run( 'git checkout %s' % branch,
                            #                prompt=True,
                            #                print_trace=True )


    def refresh( self ):
        self.checkout_branch()
        self.refresh_init_version()
        self.refresh_local_status()
        self.refresh_remote_status()
        self.refresh_changeset()
        self.refreshed = True


    #----------------------------------------------------------------------
    def get_changeset_id( self ):
        if self.changeset:
            return self.changeset.id
        return None


    #------------------------------------------------------------------
    def get_changeset_author( self ):
        return self.changeset.author


    #------------------------------------------------------------------
    def get_changeset_timestamp( self ):
        # term.printDebug( 'cs: %s' % repr( self.changeset ) )
        if self.changeset:
            return self.changeset.timestamp
        return None


    #------------------------------------------------------------------
    def get_changeset_commit_msg( self ):
        return self.changeset.commit_msg


    #----------------------------------------------------------------------
    def get_status_branch( self, remote=True ):
        if remote and self.remote_status:
            return self.remote_status.branch
        return self.local_status.branch


    #----------------------------------------------------------------------
    def is_repo_clean( self, remote=True ):
        if remote and self.remote_status:
            return self.remote_status.clean_repo
        return self.local_status.clean_repo


    #----------------------------------------------------------------------
    def is_outdated( self, other ):
        self_id = self.get_changeset_id()
        other_id = other.get_changeset_id()
        if self_id and other_id and self_id == other_id:
            return False
        self_ts = self.get_changeset_timestamp()
        other_ts = other.get_changeset_timestamp()

        if self_ts and other_ts and self_ts < other_ts:
            return True
        return None


    #----------------------------------------------------------------------


