# coding=utf-8

from fabric.context_managers import hide

from m16e import term

SRV_APACHE_RESTART              = ('sar', '', '', 'restarts apache')
INIT_SERVER                     = ('si', '', '', 'initialize server')
SRV_LIST_DISK_FREE              = ('sldf', '', '', 'list disk usage and free space')
SRV_LIST_DISK_USE               = ('sldu', '<folder>', '', 'list disk usage for <folder>')
INIT_SERVER_LIST_PACKAGES       = ('slp', '', '', 'list of packages')
INIT_SERVER_PACKAGES            = ('sid', '', '', 'initialize package deps')
INIT_SERVER_ENV                 = ('siv', '', '', 'initialize package env')
INIT_SERVER_GIT                 = ('sig0',  '', '', 'initialize git')
INIT_SERVER_GITOLITE            = ('sig1', '', '', 'install gitolite')
INIT_SERVER_GITOLITE_CONF       = ('scg', '', '', 'configure gitolite')
INIT_SERVER_W2P_REPO            = ('siw', '', '', 'initialize web2py server repo')
PURGE_SERVER                    = ('sp', '', '', 'purge server')
PURGE_SERVER_PACKAGES           = ('spd', '', '', 'purge server package deps')
SRV_POSTGRES_RESTART            = ('spr', '', '', 'restarts postgresql')
PURGE_SERVER_ENV                = ('spv', '', '', 'purge server package env')
SRV_REBOOT                      = ('sr', '', '', 'reboot server')
SET_SERVER                      = ('ss', '', '<server_name>', 'sets server <server_name> as default')
SRV_UPDATE                      = ('su', '', '', 'apt-get update && upgrade')
COMPILE_FOLDER_REPORTS          = ('scfr', '<folder>', '', 'compile reports in local <folder> in server')


INIT_CLUSTER                    = ('ci', '', '', 'initialize cluster')
PURGE_CLUSTER                   = ('cp', '', '', 'purge cluster')
SET_CLUSTER                     = ('cs', '<cluster_idx>', '<cluster_name>',
                                   'sets cluster <cluster_idx> or <cluster_name> as default')
LIST_APPS                       = ('cal', '[c]', '', 'list cluster apps ("c" for children)' )
UPGRADE_CLUSTER                 = ('cu', '[w2p_version]', '', 'upgrade web2py to version <w2p_version>' )
UPGRADE_CLUSTER_APPS            = ('cua', '<from>', '<to>', 'upgrade cluster apps from version <from> to version <to>' )
CLEAR_CLUSTER_ERRORS            = ('ccer', '[age]', '', 'clears cluster errors (age defaults to 5 days, "*" for all)' )
CLEAR_CLUSTER_SESSIONS          = ('ccse', '[age]', '', 'clears cluster sessions (age defaults to 5 days, "*" for all)')
CLEAR_CLUSTER_TMP_DIRS          = ('cctd', '[age]', '', 'clears cluster tmp dir (age defaults to 5 days, "*" for all)')
CLUSTER_SET_DEFAULT_USERS       = ('csdu', '', '', 'set default users and groups')
ADD_USERS_TO_CLUSTER            = ('cauc', '<user_list file>', '', 'add user to cluster apps (same format of init)')
ADD_GROUP_TO_CLUSTER            = ('cagc', '<role>', '<description>', 'add group to cluster apps')
CHANGE_CLUSTER_USER_MAIL        = ('ccum', '<old mail>', '<new mail>', 'change user mail')
CHANGE_CLUSTER_USER_PASS        = ('ccup', '<user mail>', '<password>', 'change user password')
CLUSTER_ADD_USER_TO_GROUP       = ('caug', '<user mail>', '<group>', 'add user to group')
CLUSTER_SYNC_FROM_PRODUCTION    = ('csfp', '', '', 'sync cluster from production')

INIT_APP                        = ('ai', '', '', 'initialize app')
INIT_APP_CHILD                  = ('aic', '<child_name>', '', 'initialize app child')
PURGE_APP                       = ('ap', '', '', 'purge app')
PURGE_APP_CHILD                 = ('apc', '<child_name>', '', 'purge app <child_name>')
SET_APP                         = ('as', '<app_idx>', '', 'sets app <app_idx> as default')
UPDATE_APP                      = ('au', '[,c]', '', 'update app (use "c" to compile reports)')
UPDATE_APP_REPO                 = ('aur', '', '', 'update app repo')
UPGRADE_APP                     = ('aua', '<from>', '<to>', 'upgrade cluster apps from version <from> to version <to>' )
UPGRADE_BLM_APP                 = ('aublm', '<org_app_name>', '', 'upgrade app <org_app_name> from belmiro 2')
UPLOAD_APP                      = ('aupload', '', '', 'uploads app as a tarball' )
RESET_APP                       = ('areset', '[<name>]', '[d|e]', 'reset app (<name> or current app); [d|e]: reset docs|ents only')
COMPILE_APP                     = ('ac', '[r|a]', '', 'compile reports or app')
LIST_APP_RELEASES               = ('alr', '', '', 'list app releases')
GET_APP_TARBALL                 = ('atget', '<app_name>', '', 'get app tarball')
CLEAR_APP_ERRORS                = ('acer', '[age]', '', 'clears errors (age defaults to 5 days)' )
CLEAR_APP_SESSIONS              = ('acse', '[age]', '', 'clears sessions (age defaults to 5 days)')
# CLEAR_APP_CHILD_ERRORS          = ('accer', '[age]', '', 'clears children errors (age defaults to 5 days)' )
# CLEAR_APP_CHILD_SESSIONS        = ('accse', '[age]', '', 'clears children sessions (age defaults to 5 days)')
CLEAR_APP_OLD_RELEASES          = ('acor', '[age]', '', 'clears apps old releases (age defaults to 5 days)')

GET_APP_I18N_FILES              = ('gif', '', '', 'gets i18n files')

PULL_DB                         = ('dpull', '[z|j]', '', 'download and restore database ("z" for gzip)')
PUSH_DB                         = ('dpush', '[z|j]', '', 'dump, upload and restore database ("z" for gzip)')
LIST_ALL_DBS                    = ('dbla', '', '', 'list all databases')
LIST_LOCAL_DBS                  = ('dbll', '', '', 'list local databases')
LIST_REMOTE_DBS                 = ('dblr', '', '', 'list remote databases')
UPGRADE_CHILD_DBS               = ('dbcup', '', '', 'update master + child databases')

GET_CUSTOMER_IP                 = ('gip', '<customer_name>', '', 'get <customer_name>\'s IP' )

QUIT                            = ('q', '', '', 'quit' )
SECTION_SERVER                  = ('.s', '', '', 'show server menu' )
SECTION_CLUSTER                 = ('.c', '', '', 'show cluster menu' )
SECTION_APP                     = ('.a', '', '', 'show app menu' )
SECTION_DATABASE                = ('.d', '', '', 'show database menu' )
SECTION_MISC                    = ('.m', '', '', 'show misc menu' )

# menu sections
SEC_SERVER = 'server'
SEC_CLUSTER = 'cluster'
SEC_APP = 'app'
SEC_DATABASE = 'database'
SEC_MISC = 'misc'


def show_server_status( server_status ):
    status = ''
    if server_status:
        status += term.fg_blue( ' Server: ' )
        status += term.fg_magenta( server_status.server_name )
        status += term.fg_blue( '\n Status: ' )
        msg = '\n    Home created: %s' % server_status.web_home_created
        if server_status.web_home_created == 'NO':
            status += term.fg_red( msg )
        else:
            status += term.fg_green( msg )
        msg = '\n    Gitolite installed: %s' % server_status.gitolite_home_created
        if server_status.gitolite_home_created == 'NO':
            status += term.fg_red( msg )
        else:
            status += term.fg_green( msg )

    print( status )
    return server_status


def show_cluster_status( cluster_status ):
    status = 'Not created'
    if cluster_status:
        status = term.fg_blue( ' Cluster: ' )
        if cluster_status.w2p_web_folder_created == 'NO' or \
                cluster_status.w2p_web_folder_created == 'NO':
            status += term.fg_red( cluster_status.cluster_name )
        else:
            status += term.fg_magenta( cluster_status.cluster_name )
        status += term.fg_blue( '\n    Status: ' )
        msg = '\n       W2p repo created: %s''' % \
              cluster_status.w2p_web_folder_created
        if cluster_status.w2p_web_folder_created == 'NO':
            status += term.fg_red( msg )
        else:
            status += term.fg_green( msg )
        msg = '\n       W2p web folder created: %s''' % \
              cluster_status.w2p_web_folder_created
        if cluster_status.w2p_web_folder_created == 'NO':
            status += term.fg_red( msg )
        else:
            status += term.fg_green( msg )
    print( status )
    return cluster_status


def show_app_status( app_status ):
    status = ''
    if app_status:
        status += term.fg_blue( ' App: ' )
        status += term.fg_magenta( ' %s ' % app_status.master_app )
        status += '\n ' + term.fg_blue( ' LOCAL: %s - %s' % (app_status.local_version,
                                                             app_status.local_version_date) )
        status += '\n    status: ' + (app_status.local_status_resumed or '')

        if app_status.repo_version:
            status += '\n ' + term.fg_green( ' REPO : %s - %s (%s)' % (app_status.repo_version,
                                                                       app_status.repo_version_date,
                                                                       app_status.app_branch) )
            status += '\n    status: ' + (app_status.remote_status_resumed or '')
            if app_status.web_version:
                status += '\n ' + term.fg_magenta( ' WEB  : %s - %s' % (app_status.web_version,
                                                                        app_status.web_version_date) )
            else:
                status += '\n ' + term.fg_red( ' WEB  :')
        else:
            status += term.fg_red( app_status.repo_msg )
    print( status )
    return app_status


def get_menu_str( option ):
    # term.printDebug( 'option: %s' % repr( option ) )
    s = option[0]
    if option[1]:
        s += ', ' + option[1]
    if option[2]:
        s += ', ' + option[2]
    s += ': '
    s = term.fg_magenta( s ) + ' ' + term.fg_blue( option[3] )
    return s



def get_server_options( cfg, server_status ):
    menu = ' >>> Options\n -- Servers --'
    if cfg.curr_section == SEC_SERVER:
        if server_status.web_home_created == 'NO':
            menu += '\n ' + get_menu_str( INIT_SERVER )
            menu += '\n ' + get_menu_str( INIT_SERVER_PACKAGES )
            menu += '\n ' + get_menu_str( INIT_SERVER_ENV )

        if server_status.web_home_created != 'NO':
            menu += '\n ' + get_menu_str( PURGE_SERVER_ENV )
        menu += '\n ' + get_menu_str( PURGE_SERVER_PACKAGES )
        menu += '\n ' + get_menu_str( PURGE_SERVER )

        if server_status.w2p_home_created == 'NO':
            menu += '\n ' + get_menu_str( INIT_SERVER_W2P_REPO )

        if server_status.gitolite_home_created == 'NO':
            menu += '\n ' + get_menu_str( INIT_SERVER_GITOLITE )

        else:
            menu += '\n ' + get_menu_str( INIT_SERVER_GITOLITE_CONF )

        menu += '\n ' + get_menu_str( INIT_SERVER_LIST_PACKAGES )
        menu += '\n ' + get_menu_str( PURGE_SERVER )

    menu += '\n ' + get_menu_str( SET_SERVER )
    menu += '\n ' + get_menu_str( SRV_APACHE_RESTART )
    menu += '\n ' + get_menu_str( SRV_POSTGRES_RESTART )
    menu += '\n ' + get_menu_str( SRV_LIST_DISK_FREE )
    menu += '\n ' + get_menu_str( SRV_LIST_DISK_USE )
    menu += '\n ' + get_menu_str( SRV_UPDATE )
    menu += '\n ' + get_menu_str( COMPILE_FOLDER_REPORTS )
    menu += '\n ' + get_menu_str( SRV_REBOOT )
    return menu


def get_cluster_options( cfg, server_status, cluster_status ):
    menu = '''
 -- Clusters --'''
    term.printDebug( 'server_status: %s' % repr( server_status ) )
    term.printDebug( 'cluster_status: %s' % repr( cluster_status ) ) #, prompt_continue=True )
    if cluster_status and server_status.web_home_created != 'NO':
        if cluster_status.w2p_web_folder_created == 'NO':
            menu += '\n' + get_menu_str( INIT_CLUSTER )
        else:
            menu += '\n' + get_menu_str( PURGE_CLUSTER )

    if server_status.web_home_created != 'NO':
        menu += '\n' + get_menu_str( SET_CLUSTER )

    menu += '\n' + get_menu_str( LIST_APPS )
    menu += '\n' + get_menu_str( UPGRADE_CLUSTER )
    menu += '\n' + get_menu_str( UPGRADE_CLUSTER_APPS )
    menu += '\n' + get_menu_str( CLEAR_CLUSTER_ERRORS )
    menu += '\n' + get_menu_str( CLEAR_CLUSTER_SESSIONS )
    menu += '\n' + get_menu_str( CLEAR_CLUSTER_TMP_DIRS )
    menu += '\n' + get_menu_str( CLUSTER_SET_DEFAULT_USERS )
    menu += '\n' + get_menu_str( ADD_USERS_TO_CLUSTER )
    menu += '\n' + get_menu_str( CHANGE_CLUSTER_USER_MAIL )
    menu += '\n' + get_menu_str( CHANGE_CLUSTER_USER_PASS )
    menu += '\n' + get_menu_str( CLUSTER_ADD_USER_TO_GROUP )
    menu += '\n' + get_menu_str( ADD_GROUP_TO_CLUSTER )
    server = cfg.get_server()
    if server.test_server:
        menu += '\n' + get_menu_str( CLUSTER_SYNC_FROM_PRODUCTION )

    return menu


def get_app_options( app_status ):
    menu = '\n  -- Apps --'
    if app_status.web_version:
        menu += '\n' + get_menu_str( UPDATE_APP )
        menu += '\n' + get_menu_str( UPGRADE_APP )
        menu += '\n' + get_menu_str( UPGRADE_BLM_APP )
        menu += '\n' + get_menu_str( COMPILE_APP )
        menu += '\n' + get_menu_str( PURGE_APP )
        menu += '\n' + get_menu_str( PURGE_APP_CHILD )
        menu += '\n' + get_menu_str( RESET_APP )
        menu += '\n' + get_menu_str( GET_APP_TARBALL )
    else:
        menu += '\n' + get_menu_str( INIT_APP )

    menu += '\n' + get_menu_str( INIT_APP_CHILD )

    menu += '\n' + get_menu_str( UPDATE_APP_REPO )
    menu += '\n' + get_menu_str( UPLOAD_APP )
    # menu += '\n' + get_menu_str( UPLOAD_APP_PRIVATE_REPORTS )

    menu += '\n' + get_menu_str( LIST_APP_RELEASES )
    menu += '\n' + get_menu_str( CLEAR_APP_ERRORS )
    menu += '\n' + get_menu_str( CLEAR_APP_SESSIONS )
    menu += '\n' + get_menu_str( CLEAR_APP_OLD_RELEASES )
    # menu += '\n' + get_menu_str( CLEAR_APP_CHILD_ERRORS )
    # menu += '\n' + get_menu_str( CLEAR_APP_CHILD_SESSIONS )

    menu += '\n' + get_menu_str( SET_APP )

    return menu


def get_db_options():
    menu = '\n  -- Databases --'
    menu += '\n' + get_menu_str( PULL_DB )
    menu += '\n' + get_menu_str( PUSH_DB )
    return menu


def show_main_menu( cfg ):
    # term.printDebug( 'selection.curr_section: %s' % repr( cfg.curr_section ) )
    with hide( 'running', 'stdout', 'stderr' ):
        app = cfg.get_app()
        app_status = app.get_app_status()

        print( '\n%s' % ('-' * 80) )
        # APPS
        show_app_status( app_status )
    # print( list_databases() )
    menu = term.fg_cyan( get_app_options( app_status ) )
    menu += term.fg_cyan( get_db_options() )
    menu += '''
     --
    '''
    menu += '%s; ' % get_menu_str( SECTION_APP )
    menu += '%s; ' % get_menu_str( SECTION_DATABASE )

    menu += '%s' % get_menu_str( QUIT )
    print( menu )

    return raw_input( "Option: " )


