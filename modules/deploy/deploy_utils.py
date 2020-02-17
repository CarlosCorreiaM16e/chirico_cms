#! /usr/bin/python
# coding=utf-8

from fabric.api import abort, run, settings, sudo, local
from fabric.colors import blue, red, green, magenta, cyan
from fabric.context_managers import hide
from fabric.contrib import console
import fnmatch
import inspect
import os
import os.path

from m16e.kommon import is_sequence

OK = 0
INFO = 10
WARN = 50
ERROR = 100

IONICE_CMD = '/usr/bin/ionice -c %d'


class PathNotFoundException( Exception ):
    pass

# ------------------------------------------------------------------
class CmdResult(object):
    # ------------------------------------------------------------------
    def __init__(self, message, error=OK):
        self.message = message
        self.error = error

    # ------------------------------------------------------------------
    def __repr__(self):
        return '{ message: %s; error: %s }' % (repr(self.message),
                                               repr(self.error))


# ----------------------------------------------------------------------
def print_result(result):
    if result.error == OK:
        print(blue(result.message))
    elif result.error <= INFO:
        print(green(result.message))
    elif result.error <= WARN:
        print(magenta(result.message))
    else:
        print(red(result.message))


# ------------------------------------------------------------------
def get_app_list(baseFolder):
    folder = baseFolder + '/src/applications'
    appList = [
        d for d in os.listdir(folder)
        if os.path.isdir(os.path.join(folder, d)) and
        d not in ['admin', 'examples', 'welcome']]
    return appList


# # ------------------------------------------------------------------
# def get_hg_module_list(folder, app_name):
#     # term.printDebug('folder: %s' % repr(folder))
#     folder += '/modules'
#     return [d for d in os.listdir(folder)
#             if os.path.isdir('%s/%s' % (folder, d))
#             and os.path.isdir('%s/%s/.hg' % (folder, d))]
#
#
# ------------------------------------------------------------------
def get_module_list(folder, app_name):
    # term.printDebug('folder: %s' % repr(folder))
    folder += '/modules'
    return [d for d in os.listdir(folder)
            if os.path.isdir('%s/%s' % (folder, d))]


# ----------------------------------------------------------------------
def find_files(dir, pattern):
    for root, dirs, files in os.walk(dir):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                yield filename


# ----------------------------------------------------------------------
def find_files_by_pattern_list(dir, pattern_list):
    #     term.printDebug( 'dir: %s' % ( repr( dir ) ) )
    for root, dirs, files in os.walk(dir):
        for basename in files:
            for pattern in pattern_list:
                if fnmatch.fnmatch(basename, pattern):
                    filename = os.path.join(root, basename)
                    yield filename


# ----------------------------------------------------------------------
def hg_init_hook(folder):
    has_hook = False
    file_exists = False
    hgrc_file = os.path.join(folder, ".hg", "hgrc")
    hg_hook = "changegroup = hg update >&2"
    if os.path.exists(hgrc_file):
        file_exists = True
        for line in open(hgrc_file):
            if hg_hook in line:
                has_hook = True
                break

    if has_hook:
        print folder + " already has hook"
    elif file_exists:
        print "+ adding hook to: " + folder
        f = file(hgrc_file, 'a')
        f.write("\n\n[hooks]\n" + hg_hook + "\n\n");
        f.close()
    else:
        print "+ creating hook in: " + folder
        f = file(hgrc_file, 'w')
        f.write("\n\n[hooks]\n" + hg_hook + "\n\n");
        f.close()


# ------------------------------------------------------------------
prompt_continue = True


# ------------------------------------------------------------------
def set_prompt_continue(cont):
    global prompt_continue
    prompt_continue = cont
    # term.printDebug( 'prompt_continue: %s' % repr( prompt_continue ) )


def get_prompt_continue():
    return prompt_continue


# ------------------------------------------------------------------
def cli_continue(msg='Continue?'):
    global prompt_continue
    if prompt_continue:
        if not console.confirm(msg, default=True):
            abort('Stopped by user')
        if console.confirm('Continue ALL?', default=False):
            prompt_continue = False


# ------------------------------------------------------------------
EX_LOCAL = 'local'
EX_RUN = 'run'
EX_SUDO = 'sudo'


def cli_execute( cmd,
                 cmd_prefix=None,
                 exec_type=EX_LOCAL,
                 user=None,
                 password=None,
                 prompt=False,
                 hide_output=None,
                 warn_only=False,
                 quiet=False,
                 print_output=True,
                 capture=True,
                 print_trace=False ):
    '''
        cmd= comand to execute
        exec_type= [ EX_LOCAL, EX_RUN, EX_SUDO ] # command type
        user=None,
        password=None,
        prompt=False,
        hide=None, [ 'everything', 'stderr', stdout' ] or
                   True for hide='everything'
        warn_only
    '''
    global prompt_continue
    # term.printDebug( 'prompt_continue: %s' % repr( prompt_continue ) )
    # term.printDebug( 'prompt: %s' % repr( prompt ) )
    if cmd_prefix:
        cmd = '%s %s' % (cmd_prefix, cmd)
    if print_trace:
        st_msg = ' -- called by:'
        for st in inspect.stack():
            if 'gluon' in st[1]:
                st_msg += '\n - (...)'
                break
            st_msg += '\n - %s:%d' % ( st[1], st[2] )
        print( magenta( st_msg ) )
    if prompt:
        if prompt_continue:
            if exec_type == EX_SUDO:
                msg = 'SUDO cmd: %s'
            else:
                msg = 'EXEC cmd: %s'

            print( cyan( msg % cmd ) )
            cli_continue('Execute command?')

    #     term.printDebug( 'cmd: %s\nhide_output: %s' % (cmd, hide_output) )
    args = []
    kwargs = {}
    if quiet:
        args.append(hide('everything'))
        warn_only = True
        print_output = False

    elif hide_output:
        if is_sequence(hide_output):
            args.append(hide(*hide_output))
            print_output &= (('stdout' in hide_output) |
                             ('everything' in hide_output) |
                             ('running' in hide_output))

        else:
            args.append(hide('everything'))
            print_output = False

    if warn_only:
        kwargs['warn_only'] = True
    if password:
        kwargs['password'] = password
    with settings(*args,
                  **kwargs):
        if exec_type == EX_SUDO:
            cmd_args = {'combine_stderr': False}
            if user:
                cmd_args['user'] = user
            ret = sudo(cmd, **cmd_args)
        else:
            if exec_type == EX_LOCAL:
                ret = local(cmd, capture=capture)
            elif exec_type == EX_RUN:
                ret = run(cmd, combine_stderr=False)

            #         with settings( password=password,
            #                        hide=hide,
            #                        warn_only=warn_only ):
            #             if user:
            #                 ret = sudo( cmd, user=user, combine_stderr=False )
            #             else:
            #                 ret = sudo( cmd, combine_stderr=False )
            #     else:
            #
            #         with settings( hide=hide,
            #                        warn_only=warn_only ):
            #             if exec_type == EX_LOCAL:
            #                 ret = local( cmd, capture=True )
            #             elif exec_type == EX_RUN:
            #                 ret = run( cmd, combine_stderr=False )

                # term.printDebug( 'ret: %s' % repr( ret ) )
    if print_output:
        print(blue(ret.stdout))
        print(red(ret.stderr or 'OK'))
    if prompt:
        cli_continue()
    return ret


# ------------------------------------------------------------------
def cli_sudo_run( cmd,
                  cmd_prefix=None,
                  user=None,
                  password=None,
                  quiet=False,
                  prompt=False,
                  print_trace=True,
                  use_ionice=3 ):
    if quiet:
        hide_output = 'everything'
        quiet = quiet
        print_output = False
    else:
        hide_output = None
        warn_only = False
        quiet = quiet
        print_output = True

    if use_ionice:
        cmd = (IONICE_CMD % use_ionice) + ' ' + cmd
    ret = cli_execute( cmd,
                       cmd_prefix=cmd_prefix,
                       exec_type=EX_SUDO,
                       user=user,
                       password=password,
                       hide_output=hide_output,
                       quiet=quiet,
                       print_output=print_output,
                       prompt=prompt,
                       print_trace=print_trace )
    return ret

    #     global prompt_continue
    #     if prompt:
    #         if prompt_continue:
    #             print( cyan( 'SUDO cmd: %s' % cmd ) )
    #         cli_continue( 'Execute command?' )
    #     cmd = cmd
    #     with settings( password=password ):
    #         if user:
    #             ret = sudo( cmd, user=user, combine_stderr=False )
    #         else:
    #             ret = sudo( cmd, combine_stderr=False )
    #     print( blue( ret.stdout ) )
    #     print( red( ret.stderr ) )
    #     if prompt:
    #         cli_continue()
    # return ret


# ------------------------------------------------------------------
def cli_run( cmd,
             cmd_prefix=None,
             quiet=False,
             prompt=False,
             print_trace=False ):
    ret = cli_execute( cmd,
                       cmd_prefix=cmd_prefix,
                       exec_type=EX_RUN,
                       quiet=quiet,
                       prompt=prompt,
                       print_trace=print_trace )
    return ret


#     global prompt_continue
#     if prompt:
#         if prompt_continue:
#             print( cyan( 'RUN cmd: %s' % cmd ) )
#         cli_continue( 'Execute command?' )
#     cmd = cmd
#     ret = run( cmd, combine_stderr=False )
#     print( blue( ret.stdout ) )
#     print( red( ret.stderr ) )
#     if prompt:
#         cli_continue()
#     return ret

# ------------------------------------------------------------------
def cli_local( cmd,
               cmd_prefix=None,
               prompt=False,
               capture=True,
               quiet=False ):
    ret = cli_execute( cmd,
                       cmd_prefix=cmd_prefix,
                       exec_type=EX_LOCAL,
                       prompt=prompt,
                       capture=capture,
                       quiet=quiet )
    return ret

#     global prompt_continue
#     if prompt:
#         if prompt_continue:
#             print( cyan( 'LOCAL cmd: %s' % cmd ) )
#         cli_continue( 'Execute command?' )
#     cmd = cmd
#     ret = local( cmd, capture=True )
#     print( blue( ret.stdout ) )
#     print( red( ret.stderr ) )
#     if prompt:
#         cli_continue()
#     return ret


