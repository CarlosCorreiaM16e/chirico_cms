# coding=utf-8

from fabric.context_managers import settings, lcd, cd
from fabric.operations import put

from deploy_utils import cli_run, cli_local, cli_sudo_run, cli_continue
from m16e import term


def db_exists( server,
               db_name ):
    with settings( host_string=server.get_user_host_string(),
                   warn_only = True ):
        result = cli_run( '''psql -tAc "select 1 from pg_database where datname='%s'"''' %
                          db_name )
        term.printDebug( 'result: %s' % repr( result ) )
        return bool( result )


def drop_db( server,
             db_name ):
    term.printDebug( 'dropdb' )
    with settings( host_string=server.get_user_host_string(),
                   warn_only = True ):
        result = cli_run( '''psql -tAc "select 1 from pg_database where datname='%s'"''' %
                          db_name,
                          prompt=True )
        term.printDebug( 'result: %s' % repr( result ) )
        cli_continue( 'Continue?' )
        if result:
            server.pg_ctl( 'restart' )
            cli_run( 'dropdb %s' % db_name,
                     prompt=True )


def push_db( cfg, db_name ):
    server = cfg.get_server()
    folder = '~/tmp/downloads'
    sql_filename = 'dump-%s.sql' % db_name
    cli_local( 'mkdir -p %s' % folder )
    if cfg.db_compression == 'z':
        ext = 'tgz'
    elif cfg.db_compression == 'j':
        ext = 'bz2'
    else:
        ext = 'tar'
    with lcd( folder ):
        tarball = '%s.tar.%s' % (sql_filename, ext)
        cli_local( 'pg_dump -C %s -f %s' % (db_name, sql_filename) )
        cli_local( 'tar %scvf %s %s' % (cfg.db_compression, tarball, sql_filename) )

    with settings( host_string=server.get_user_host_string(),
                   password=server.sys_password ):
        cli_run( 'mkdir -p tmp' )
        tarball = '%s.tar.%s' % (sql_filename, ext)
        put( '%s/%s' % (folder, tarball),
             'tmp/%s' % tarball )
        with cd( 'tmp' ):
            filename = cli_run( 'tar %sxvfm %s' % (cfg.db_compression, tarball) )
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
                drop_db( server, db_name )
            cli_run( 'psql -f %s -v ON_ERROR_STOP=1' % filename )
