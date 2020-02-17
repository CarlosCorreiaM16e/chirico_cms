# -*- coding: utf-8 -*-

import sys
from fabric.contrib import console

from deploy import deploy_menu, db_utils, deploy_utils
from deploy.app import AppExistsException
from deploy.config import Config
from m16e import term

__author__ = 'carlos@memoriapersistente.pt'
__version__ = "0.1.0"


def init_app( cfg ):
    app = cfg.get_app()
    msg = app.init_remote_repo()
    if msg:
        print( msg )
        ret = console.prompt( 'Delete Skip Abort', default='d' )
        if ret == 'a':
            return
        app.init_remote_repo()
    app.init_web_repo()
    db_name = cfg.get_db_name( app.app_name )
    server = cfg.get_server()
    server.pg_ctl( 'restart' )
    if deploy_utils.get_prompt_continue() and console.confirm( 'Drop DB (%s) and upload?' % db_name, default=True ):
        server.push_db( db_name )
    server.apache_ctl( 'restart' )


def init_app_child( cfg, child_name ):
    app = cfg.get_app()
    server = cfg.get_server()
    db_name = cfg.get_db_name( child_name )
    try:
        app.init_child_app( child_name )
    except AppExistsException as e:
        print( e )
        force = raw_input( 'Force (y/N)?' )
        if force and force.lower().startswith( 'y' ):
            app.purge_child_app( child_name )
            db_utils.drop_db( server, db_name )
            app.init_child_app( child_name )

    if deploy_utils.get_prompt_continue() and console.confirm( 'Drop DB (%s) and upload?' % db_name, default=True ):
        server.pg_ctl( 'restart' )
        db_utils.drop_db( server, db_name )
        db_utils.push_db( cfg, child_name )
    server.apache_ctl( 'restart' )


def update_app( cfg, repo_only=False ):
    app = cfg.get_app()
    app.update_remote_repo()
    app.upgrade_web_repo()
    cfg.get_server().apache_ctl( 'restart' )


def purge_app( cfg ):
    app = cfg.get_app()
    if deploy_utils.get_prompt_continue() and console.confirm( 'Purge app "%s"' % app.app_name, default=False ):
        msg = app.purge_web_folder()
        if msg:
            print( msg )
        msg = app.purge_remote_repo()
        if msg:
            print( msg )
        db_name = cfg.get_db_name( app.app_name )
        db_utils.drop_db( cfg.get_server(), db_name )


def init_cluster( cfg ):
    cluster = cfg.get_cluster()
    msg = cluster.init_web2py_from_zip()
    if msg:
        print( msg )

    # term.printDebug( 'msg: %s' % repr( msg ),
    #                  prompt_continue=True )
    msg = cluster.init_web2py()
    if msg:
        print( msg )
        if msg.startswith( 'ERROR:->' ):
            if console.confirm( 'Abort?', default=False ):
                return

    cluster.define_web2py_admin_password()
    if console.confirm( 'Create site-available file?', default=False ):
        cluster.create_site_available()
    server = cfg.get_server()
    server.apache_ctl( 'stop' )
    server.apache_ctl( 'start' )


def clear_app_errors( cfg, age=5 ):
    '''
    clear_app_errors(  )
    '''
    app = cfg.get_app()
    f_list = app.list_error_files( age )
    print( 'Delete app errors: ' + app.app_name )
    if not f_list:
        print( 'no files to remove' )
    else:
        for e in f_list.splitlines():
            print('  - ' + e)
        op = raw_input( 'Continue (Y/n)?' )
        if op != 'n':
            app.delete_error_files( age )


def clear_app_sessions( cfg ):
    '''
    clear_app_sessions()
    '''
    app = cfg.get_app()
    op = raw_input( 'Continue (Y/n)?' )
    if op != 'n':
        app.remove_sessions()


def clear_app_old_releases( cfg, age=5, preserve=3 ):
    '''
    clear_app_old_releases(  )
    '''
    app = cfg.get_app()
    rel_list = app.clear_old_releases( age=age, preserve=preserve )


def get_app_i18n_files( cfg ):
    app = cfg.get_app()
    app.get_app_i18n_files()


def upgrade_app( cfg, v_from, v_to ):
    app = cfg.get_app()
    term.printDebug( 'v_from: %s, v_to: %s' % (repr( v_from ), repr( v_to ) ) )
    app.upgrade_app( v_from, v_to )


def pull_db( cfg ):
    app = cfg.get_app()
    app.pull_db()


def push_db( cfg ):
    app = cfg.get_app()
    app.push_db()


def execute( cfg ):
    s = "args (" + str( len( sys.argv ) ) + "): " + str( sys.argv )
    print()
    print( ">" * len( s ) )
    print( s )
    print( ">" * len( s ) )
    print()
    cfg.curr_section = deploy_menu.SEC_APP
    op = deploy_menu.show_main_menu( cfg )
    while op != deploy_menu.QUIT[ 0 ]:
        args = [ a.strip() for a in op.split( "," ) ]
        if args[0] == deploy_menu.INIT_APP[0 ]:
            init_app( cfg )

        elif args[ 0 ] == deploy_menu.UPDATE_APP[ 0 ]:
            update_app( cfg )

        elif args[0] == deploy_menu.PURGE_APP[0 ]:
            purge_app( cfg )

        elif args[0] == deploy_menu.INIT_CLUSTER[0 ]:
            init_cluster( cfg )

        elif args[0] == deploy_menu.CLEAR_APP_ERRORS[0 ]:
            clear_app_errors( cfg )

        elif args[0] == deploy_menu.CLEAR_APP_SESSIONS[0 ]:
            clear_app_sessions( cfg )

        elif args[ 0 ] == deploy_menu.CLEAR_APP_OLD_RELEASES[ 0 ]:
            if len( args ) > 1:
                clear_app_old_releases( cfg, age=int( args[ 1 ] ) )
            else:
                clear_app_old_releases( cfg )

        elif args[ 0 ] == deploy_menu.UPGRADE_APP[ 0 ]:
            upgrade_app( cfg, args[ 1 ], args[ 2 ] )

        elif args[ 0 ] == deploy_menu.PULL_DB[ 0 ]:
            pull_db( cfg )

        elif args[ 0 ] == deploy_menu.PUSH_DB[ 0 ]:
            push_db( cfg )

        elif args[ 0 ] == deploy_menu.GET_APP_I18N_FILES[ 0 ]:
            get_app_i18n_files( cfg )

        op = deploy_menu.show_main_menu( cfg )

        # term.printDebug( 'args: %s' % (repr(args) ) )
        # term.printLog( 'op: %s' % (op ) )
        # if args[ 0 ] == SRV_APACHE_RESTART[ 0 ]:
        #     apache_ctl( 'restart' )
        #
        # elif args[ 0 ] == SRV_POSTGRES_RESTART[ 0 ]:
        #     postgres_ctl( 'restart' )
        #
        # elif args[ 0 ] == SRV_LIST_DISK_FREE[ 0 ]:
        #     list_server_disk_free()
        #     list_server_disk_usage()
        #
        # elif args[ 0 ] == SRV_LIST_DISK_USE[ 0 ]:
        #     folder = args[ 1 ]
        #     # term.printDebug( 'folder: %s' % folder )
        #     list_server_disk_usage( folder=folder )
        #
        # elif args[ 0 ] == COMPILE_FOLDER_REPORTS[ 0 ]:
        #     folder = args[ 1 ]
        #     # term.printDebug( 'folder: %s' % folder )
        #     compile_folder_reports( folder, server_name=selection.server.srv_ctx )
        #
        # elif args[ 0 ] == SRV_UPDATE[ 0 ]:
        #     server_upgrade_pkg()
        #
        # elif args[ 0 ] == SRV_REBOOT[ 0 ]:
        #     server_reboot()
        #
        # elif args[0] == INIT_SERVER_LIST_PACKAGES[0]:
        #     list_server_packages()
        #
        # elif args[0] == INIT_SERVER_PACKAGES:
        #     init_server_packages( yes_to_all=yes_to_all )
        #
        # elif args[0] == INIT_SERVER_ENV[0]:
        #     init_server_env()
        #
        # elif args[0] == INIT_SERVER_GIT[0]:
        #     init_server_env_git()
        #
        # elif args[0] == INIT_SERVER_GITOLITE[0]:
        #     init_server_env_gitolite_step_1( yes_to_all=yes_to_all )
        #
        # elif args[0] == INIT_SERVER_GITOLITE_CONF[0]:
        #     init_server_env_gitolite_step_2( yes_to_all=yes_to_all )
        #
        # elif args[0] == INIT_SERVER_W2P_REPO[0]:
        #     init_server_web2py_repo()
        #     # init_server_env_gitweb( yes_to_all=yes_to_all )
        #
        # elif args[0] == INIT_SERVER[0]:
        #     init_server_packages( yes_to_all=yes_to_all )
        #     init_server_env()
        #
        # elif args[0] == PURGE_SERVER_PACKAGES[0]:
        #     purge_server_packages( yes_to_all=yes_to_all )
        #
        # elif args[0] == PURGE_SERVER_ENV[0]:
        #     purge_server_env( yes_to_all=yes_to_all )
        #
        # elif args[0] == PURGE_SERVER[0]:
        #     purge_server_packages( yes_to_all=yes_to_all )
        #     purge_server_env( yes_to_all=yes_to_all )
        #
        # elif args[0] == SET_CLUSTER[0]:
        #     cl_list = sorted( selection.server.srv_ctx.clusters.clusters.keys() )
        #     cluster = cl_list[ int( args[ 1 ] ) - 1 ]
        #     set_cluster( cluster )
        #
        # elif args[0] == INIT_CLUSTER[0]:
        #     init_cluster( yes_to_all=yes_to_all )
        #
        # elif args[ 0 ] == UPGRADE_CLUSTER[ 0 ]:
        #     upgrade_cluster( yes_to_all=yes_to_all )
        #
        # elif args[0] == PURGE_CLUSTER[0]:
        #     purge_cluster( yes_to_all=yes_to_all )
        #
        # elif args[0] == CLEAR_APP_ERRORS[0]:
        #     clear_app_errors()
        #
        # elif args[0] == CLEAR_APP_SESSIONS[0]:
        #     clear_app_sessions()
        #
        # elif args[0] == CLEAR_CLUSTER_ERRORS[0]:
        #     if len( args ) > 1:
        #         clear_cluster_errors( age=args[ 1 ] )
        #     else:
        #         clear_cluster_errors()
        #
        # elif args[0] == CLEAR_CLUSTER_SESSIONS[0]:
        #     if len( args ) > 1:
        #         clear_cluster_sessions( age=args[ 1 ] )
        #     else:
        #         clear_cluster_sessions()
        #
        # elif args[ 0 ] == CLEAR_CLUSTER_TMP_DIRS[ 0 ]:
        #     if len( args ) > 1:
        #         clear_cluster_tmp_dirs( age=args[ 1 ] )
        #     else:
        #         clear_cluster_tmp_dirs()
        #
        # elif args[ 0 ] == CLEAR_APP_OLD_RELEASES[ 0 ]:
        #     if len( args ) > 1:
        #         clear_app_old_releases( age=int( args[ 1 ] ) )
        #     else:
        #         clear_app_old_releases()
        #
        # elif args[ 0 ] == LIST_APPS[ 0 ]:
        #     children = None
        #     if len( args ) > 1:
        #         children = bool( args[ 1 ] == 'c' )
        #     list_cluster_apps( children=children, yes_to_all=yes_to_all )
        #
        # elif args[ 0 ] == UPGRADE_CLUSTER_APPS[ 0 ]:
        #     upgrade_cluster_apps( args[ 1 ], args[ 2 ] )
        #
        # elif args[ 0 ] == ADD_USERS_TO_CLUSTER[ 0 ]:
        #     u_list_file = None
        #     if len( args ) > 1:
        #         u_list_file = args[ 1 ]
        #     add_users_to_cluster( u_list_file )
        #
        # elif args[ 0 ] == CLUSTER_SET_DEFAULT_USERS[ 0 ]:
        #     add_default_users_to_cluster()
        #
        # elif args[ 0 ] == CLEAR_CLUSTER_SESSIONS[ 0 ]:
        #     clear_cluster_sessions()
        #
        # elif args[ 0 ] == CHANGE_CLUSTER_USER_MAIL[ 0 ]:
        #     change_cluster_user_mail( args[ 1 ], args[ 2 ] )
        #
        # elif args[ 0 ] == CHANGE_CLUSTER_USER_PASS[ 0 ]:
        #     change_cluster_user_pass( args[ 1 ], args[ 2 ] )
        #
        # elif args[ 0 ] == CLUSTER_ADD_USER_TO_GROUP[ 0 ]:
        #     cluster_add_user_to_group( args[ 1 ], args[ 2 ] )
        #
        # elif args[ 0 ] == ADD_GROUP_TO_CLUSTER[ 0 ]:
        #     add_group_to_cluster( args[ 1 ], args[ 2 ] )
        #
        # elif args[ 0 ] == CLUSTER_SYNC_FROM_PRODUCTION[ 0 ]:
        #     if selection.server.srv_ctx.test_server:
        #         sync_cluster_from_production()
        #
        # elif args[0] == SET_APP[0]:
        #     cluster = selection.server.srv_ctx.clusters.get_cluster( selection.cluster )
        #     term.printDebug( 'cluster: %s' % repr( cluster ) )
        #     app_list = cluster.get_sorted_cluster_app_list()
        #     app = app_list[ int( args[ 1 ] ) - 1 ]
        #     set_app( app )
        #
        # elif args[0] == 'iag':
        #     init_app_repo()
        #
        # elif args[0] == INIT_APP[0]:
        #     init_app( yes_to_all=yes_to_all )
        #
        # elif args[ 0 ] == UPDATE_APP[ 0 ]:
        #     compile_jasper = False
        #     if len( args ) > 1:
        #         compile_jasper = args[ 1 ]
        #     update_app( compile_jasper=compile_jasper,
        #                 yes_to_all=yes_to_all )
        #
        # elif args[ 0 ] == COMPILE_APP[ 0 ]:
        #     compile_app( compile_reports=True )
        #
        # elif args[ 0 ] == UPDATE_APP_REPO[ 0 ]:
        #     update_app( repo_only=True )
        #
        # elif args[ 0 ] == UPLOAD_APP[ 0 ]:
        #     upload_app( yes_to_all=yes_to_all )
        #
        # # elif args[ 0 ] == UPLOAD_APP_PRIVATE_REPORTS[ 0 ]:
        # #     upload_app_private_reports( args[ 1 ] )
        #
        # elif args[ 0 ] == UPGRADE_BLM_APP[ 0 ]:
        #     org_db_name = args[ 1 ]
        #     upgrade_app_from_v2( org_db_name )
        #
        # elif args[ 0 ] == PURGE_APP[ 0 ]:
        #     purge_app()
        #
        # elif args[ 0 ] == PURGE_APP_CHILD[ 0 ]:
        #     purge_app_child( args[1] )
        #
        # elif args[ 0 ] == RESET_APP[ 0 ]:
        #     app_name = None
        #     reset_docs = False
        #     reset_ents = False
        #     if len( args ) > 1:
        #         app_name = args[ 1 ]
        #         if len( args ) > 2:
        #             r = args[ 2 ]
        #             term.printDebug( 'r: %s' % r )
        #             if 'd' in r:
        #                 reset_docs = True
        #             if 'e' in r:
        #                 reset_ents = True
        #     reset_app( app_name, reset_docs=reset_docs, reset_ents=reset_ents )
        #
        # elif args[0] == INIT_APP_CHILD[0]:
        #     init_app_child( args[1], yes_to_all=yes_to_all )
        #
        # elif args[ 0 ] == LIST_APP_RELEASES[ 0 ]:
        #     list_app_releases( yes_to_all=yes_to_all )
        #
        # elif args[ 0 ] == GET_APP_TARBALL[ 0 ]:
        #     app_name = None
        #     if len( args ) > 1:
        #         app_name = args[ 1 ]
        #     get_app_tarball( app_name=app_name )
        #
        # elif args[0] == LIST_ALL_DBS[0]:
        #     print( list_databases( 'local' ) )
        #     print( list_databases( 'remote' ) )
        #
        # elif args[0] == LIST_LOCAL_DBS[0]:
        #     print( list_databases( 'local' ) )
        #
        # elif args[0] == LIST_REMOTE_DBS[0]:
        #     print( list_databases( 'remote' ) )
        #
        # elif args[ 0 ] == GET_CUSTOMER_IP[ 0 ]:
        #     customer_name = args[ 1 ]
        #     get_customer_ip( customer_name )
        #
        # elif args[ 0 ] == SECTION_SERVER[ 0 ]:
        #     selection.curr_section = SEC_SERVER
        #
        # elif args[ 0 ] == SECTION_CLUSTER[ 0 ]:
        #     selection.curr_section = SEC_CLUSTER
        #
        # elif args[ 0 ] == SECTION_APP[ 0 ]:
        #     selection.curr_section = SEC_APP
        #
        # elif args[ 0 ] == SECTION_DATABASE[ 0 ]:
        #     selection.curr_section = SEC_DATABASE
        #
        # elif args[ 0 ] == SECTION_MISC[ 0 ]:
        #     selection.curr_section = SEC_MISC
        #
        # op = show_main_menu()

        if op:
            print( "op: " + op )


def usage():
    print( "Usage for " + sys.argv[0] + " version " + __version__ + ":" )
    print( sys.argv[0] + " [ -h ]" )
    # print( sys.argv[0] + " -s: sync backup from <server> <cluster>" )
    print( sys.argv[0] + " [--test] <config_file>" )
    print( sys.argv[0] + " " + deploy_menu.INIT_CLUSTER[0] + " <config_file>" )
    print( sys.argv[0] + " " + deploy_menu.INIT_APP[0] + " <config_file>" )
    print( sys.argv[0] + " " + deploy_menu.INIT_APP_CHILD[0] + " <app_name> <config_file>" )
    print( sys.argv[0] + " " + deploy_menu.UPDATE_APP[0] + " <config_file>" )
    print( sys.argv[0] + " " + deploy_menu.UPGRADE_APP[0] + " <from> <to> <config_file>" )
    print( sys.argv[0] + " " + deploy_menu.CLEAR_APP_SESSIONS[0] + " <config_file>" )
    print( sys.argv[0] + " " + deploy_menu.CLEAR_APP_ERRORS[0] + " <config_file>" )
    print( sys.argv[0] + " " + deploy_menu.CLEAR_APP_OLD_RELEASES[0] + " <config_file>" )
    print( sys.argv[0] + " " + deploy_menu.GET_APP_I18N_FILES[0] + " <config_file>" )


def run_app():
    # term.printDebug( 'args: %s' % repr( sys.argv ) )
    if len( sys.argv ) > 1:
        # help
        if sys.argv[ 1 ] == '-h':
            usage()
        else:
            cfg = Config( sys.argv[ -1 ] )
            server = cfg.get_server()
            server.get_ip()
            idx = 1
            test_server = False
            if sys.argv[ idx ] == '--test':
                test_server = True
                idx += 1
            if sys.argv[ idx ] == '-y':
                deploy_utils.set_prompt_continue( False )
                idx += 1
            if sys.argv[ idx ] == deploy_menu.INIT_CLUSTER[0]:
                init_cluster( cfg )
            elif sys.argv[ idx ] == deploy_menu.INIT_APP[0]:
                init_app( cfg )
            elif sys.argv[ idx ] == deploy_menu.INIT_APP_CHILD[0]:
                init_app_child( cfg, sys.argv[ idx + 1 ] )
            elif sys.argv[ idx ] == deploy_menu.UPDATE_APP[ 0 ]:
                update_app( cfg )
            elif sys.argv[ idx ] == deploy_menu.UPGRADE_APP[ 0 ]:
                upgrade_app( cfg, sys.argv[ idx + 1 ], sys.argv[ idx + 2 ] )
            elif sys.argv[ idx ] == deploy_menu.CLEAR_APP_ERRORS[ 0 ]:
                clear_app_sessions( cfg )
            elif sys.argv[ idx ] == deploy_menu.CLEAR_APP_SESSIONS[ 0 ]:
                clear_app_errors( cfg )
            elif sys.argv[ idx ] == deploy_menu.CLEAR_APP_OLD_RELEASES[ 0 ]:
                clear_app_old_releases( cfg )
            elif sys.argv[ idx ] == deploy_menu.GET_APP_I18N_FILES[ 0 ]:
                get_app_i18n_files( cfg )
            else:
                execute( cfg )
    else:
        usage()

if __name__ == "__main__":
    run_app()

