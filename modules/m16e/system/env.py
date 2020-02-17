# -*- coding: utf-8 -*-

from gluon import current
from m16e.files import fileutils

DEV_SERVERS = [ 'zappa', 'trane' ]


def is_dev_server():
    srv_name = get_server_name()
    return srv_name in DEV_SERVERS


def get_http_hostname():
    request = current.request
    if request.wsgi:
        return request.wsgi.environ[ 'HTTP_HOST' ]
    return current.server_name


def get_server_name():
    request = current.request
    if request.wsgi:
        return request.wsgi.environ[ 'SERVER_NAME' ]
    server_name = fileutils.read_file( '/etc/hostname' )
    return server_name.strip()


def get_path_info():
    request = current.request
    if request.wsgi:
        return request.wsgi.environ[ 'PATH_INFO' ]
    return request.env.path_info
