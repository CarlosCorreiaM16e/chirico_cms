#! /usr/bin/python

import os
import subprocess
import threading


debug = True

#----------------------------------------------------------------------
# based on code from:
# http://stackoverflow.com/questions/1191374/subprocess-with-timeout

class Command(object):
    def __init__( self, cmd ):
        self.cmd = cmd
        self.process = None

    def run( self, timeout ):
        # timeout in seconds
        def target():
            print( 'Thread started (pwd: %s)' % os.getcwd() )
            print( 'Thread started: cmd= %s' % ( repr( self.cmd ) ) )
#            self.process = subprocess.Popen( self.cmd, shell = True )
            self.process = subprocess.Popen(
                self.cmd, bufsize = -1,
                stderr = subprocess.STDOUT )

            self.process.communicate()
            print( 'Thread finished: cmd= %s' % ( repr( self.cmd ) ) )

        thread = threading.Thread( target = target )
        thread.start()

        thread.join( timeout )
        if thread.is_alive():
            print( 'Killing thread: cmd= %s' % ( repr( self.cmd ) ) )
            print 'Terminating process'
            self.process.terminate()
            thread.join()
        print(
            'Exiting thread: cmd= %s\nself.process: %s' %
            ( repr( self.cmd ), repr( self.process ) ) )

#command = Command("echo 'Process started'; sleep 2; echo 'Process finished'")
#command.run(timeout=3)
#command.run(timeout=1)

#----------------------------------------------------------------------
def execInShell( execute ):
    cmd = Command( execute )
    cmd.run( 30 )
    

#----------------------------------------------------------------------
def execCall( execute ):
    command = execute
    if debug:
        text = "commands:\n%s\nexecuting: %s" % ( repr( command ), " ".join( command ) )
        print( text )
    proc = subprocess.Popen( command,
                             stderr=subprocess.STDOUT,
                             stdout=subprocess.PIPE )
    out, err = proc.communicate()
    if err:
        print "ERROR>>> " + str( err )
        #sys.exit( 1 )
    return out


