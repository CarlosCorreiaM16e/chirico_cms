# -*- coding: utf-8 -*-
#! /usr/bin/python

import ast
import errno
import fnmatch
import re
import tempfile

import os.path
import shutil

from gluon import current, URL, A, DIV
from m16e import term, htmlcommon
from m16e.decorators import deprecated


def findFiles( dir, pattern ):
    for root, dirs, files in os.walk( dir ):
        for basename in files:
            if fnmatch.fnmatch( basename, pattern ):
                filename = os.path.join( root, basename )
                yield filename


def findFilesByPatternList( dir, patternList ):
    for root, dirs, files in os.walk( dir ):
        for basename in files:
            for pattern in patternList:
                if fnmatch.fnmatch( basename, pattern ):
                    filename = os.path.join( root, basename )
                    yield filename


def catFile( file ):
    lines = readFilelines( file )
    for l in lines:
        print( l.strip() )


def read_file_lines( file, keep_newlines=False ):
    f = open( file, "r" )
    if keep_newlines:
        lines = f.readlines()
    else:
        lines = f.read().splitlines()
    f.close()
    return lines


def read_file( file ):
    f = open( file, "r" )
    lines = f.read()
    f.close()
    return lines


def read_data_file( file ):
    f = open( file, "r" )
    s = f.read()
    f.close()
    return ast.literal_eval( s )


def file_exists( filename ):
    return os.path.isfile( filename )


def readPropertiesFile( file ):
    f = open( file, "r" )
    lines = f.readlines()
    f.close()
    props = {}
    for line in lines:
        idx = line.find( "#" )
        if idx >= 0:
            line = line[:idx].strip()
        if line.find( "=" ) > 1:
            a = line.split( "=" )
            key = a[0].strip()
            props[key] = a[1].strip()
    return props


def write_file( file, text ):
    f = open( file, "w" )
    f.write( text )
    f.close()


def write_tmp_file( content, mode='wt', suffix='', prefix='', dir=None, delete=False ):
    f = tempfile.NamedTemporaryFile( mode=mode, suffix=suffix, prefix=prefix, dir=dir, delete=delete )
    filename = f.name
    term.printDebug( 'filename: %s' % repr( filename ) )
    f.write( content )
    f.close()
    # term.printDebug( 'f: %s' % f )
    return filename


def mkdirs( path, throwError = False ):
    try:
        os.makedirs( path )
    except OSError as e:
        if e.errno == errno.EEXIST:
            pass
        elif throwError:
            raise


def joinPath( pathList ):
    path = ''
    for p in pathList:
        path = os.path.join( path, p )
    return path


def get_package_version_info( folder = '.' ):
#     term.printDebug( 'folder: %s' % repr( folder ) )
    init_file = os.path.join( folder, '__init__.py' )
#     term.printDebug( 'init_file: %s' % repr( init_file ) )
    lines = read_file_lines( init_file )

    v_info = {}
    for i in range( len( lines ) ):
        line = lines[i]
        if line.startswith( '__version__' ):
            l_value = line.split( '=' )[1].strip().replace( '\'', '"' ).replace( '"', '' )
            v_array = [x for x in l_value.split( '.' )]
            v_info[ 'major' ] = v_array[ 0 ]
            v_info[ 'minor' ] = v_array[ 1 ]
            v_info[ 'revision' ] = v_array[ 2 ]
        elif line.startswith( '__version_date__' ):
            l_value = line.split( '=' )[1].strip().replace( '\'', '"' ).replace( '"', '' )
            v_info[ 'date' ] = htmlcommon.parse_date( l_value )
            break
    return v_info


def get_w2p_full_path():
    request = current.request
    return request.global_settings.applications_parent


def copy_file_to_static_tmp( pathname ):
    T = current.T
    request = current.request
    term.printDebug( 'pathname: %s' % repr( pathname ) )
    filename = os.path.basename( pathname )
    st_filename = os.path.join( request.folder, 'static', 'tmp', filename )
    term.printDebug( 'st_filename: %s' % repr( st_filename ) )
    shutil.copyfile( pathname, st_filename )
    url = URL( 'static', 'tmp/%s' % filename )
    link = A( filename, _href=url )
    div = DIV( T( 'File generated as' ) + ': ', link )
    return (div, link, url)


@deprecated( 'read_file_lines( file )' )
def readFilelines( file ):
    f = open( file, "r" )
    lines = f.readlines()
    f.close()
    return lines


@deprecated( 'write_file( file, text )' )
def writeFile( file, text ):
    f = open( file, "w" )
    f.write( text )
    f.close()


@deprecated( 'read_data_file( file )' )
def readDataFile( file ):
    return read_data_file( file )


def filename_sanitize( filename ):
    f, ext = filename.rsplit( '.', 1 )
    term.printDebug( 'f: [%s], ext: [%s]' % (f, ext) )
    import unidecode
    f = unidecode.unidecode( f.decode( 'utf-8' ) )
    f = re.sub( r'\W', '-', f )
    return f + '.' + ext.lower()
    # c_list = ' |!"#$%&/()[]{}=?\'»«*ºª^~<>\\,;:'
    # for c in c_list:
    #     filename = filename.replace( c, '-')
    # f, ext = filename.rsplit( '.', 1 )
    # return f + '.' + ext.lower()


def move_file( old_pathname=None,
               new_pathname=None ):
    new_path, new_filename = new_pathname.rsplit( '/', 1 )
    if not os.path.exists( new_path ):
        os.makedirs( new_path )
    shutil.move( old_pathname, new_pathname )


