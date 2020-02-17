# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

from gluon import current
from m16e.kommon import DATE
from m16e.user_factory import is_in_group
from m16e.kommon import K_ROLE_DEVELOPER, K_ROLE_EDITOR

if 0:
    import gluon.languages.translator as T

    import gluon
    from gluon.tools import Auth
    from gluon.html import URL
    from gluon.html import SPAN

    global auth; auth = gluon.tools.Auth()
    global cache; cache = gluon.cache.Cache()
    global crud; crud = gluon.tools.Crud()
    global db; db = gluon.sql.DAL()
    global request; request = gluon.globals.Request()
    global response; response = gluon.globals.Response()
    global service; service = gluon.tools.Service()
    global session; session = gluon.globals.Session()


test_env = db._uri.endswith( '_test' )
title = current.app_config.take( 'theme.title' )

response.navbar_class = 'navbar-inner'
if test_env:
    title += ' (%s)' % T( 'testing environment' )
    response.navbar_class += ' test_env'
response.title = title
response.subtitle = current.app_config.take( 'theme.subtitle' )

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Carlos Correia <carlos@m16e.com>'
response.meta.description = 'Your Free CMS System'
response.meta.keywords = 'web2py, python, frameworks'
response.meta.generator = 'Web2py Web Framework'
response.meta.copyright = 'Copyright 2011-%d' % DATE.today().year

## your http://google.com/analytics id
response.google_analytics_id = None

#########################################################################
## this is the main application menu add/remove items as required
#########################################################################

path_info = URL()

response.menu += [
    ( T( 'Home' ), False, URL( c='default', f='set_session_anon' ), [] ),
]


if auth.user:
    response.menu += [
        ( T( 'Forum' ), False, URL( 'forum', 'open_discussions' ), [ ]),
        ( T( 'My Data' ), False, URL( 'user', 'mydata' ), [] ),
    ]


if is_in_group( K_ROLE_EDITOR ):
    response.menu += [
        ( T( 'Management' ), False, None, [
            (T( 'Pages' ), False, URL( c='page', f='index' ), []),
            (T( 'Blocks' ), False, URL( c='block', f='index' ), [ ]),
            (T( 'Compose new page' ), False, URL( c='page', f='composer', args = [ 0 ] ), [] ),
            (T( 'Image gallery' ), False, URL( c='gallery', f='grid' ), []),
            (T( 'Forum' ), False, URL( 'forum', 'index' ), [ ]),
            (T( 'Users' ), False, URL( c='user_admin', f='index' ), [ ]),
            (T( 'Page stats' ), False, URL( c='page_stats', f='charts' ), [ ]),
            (T( 'Page stats (detailed)' ), False, URL( c='page_stats', f='totals' ), [ ]),
            (T( 'User messages' ), True, URL( c='user_message', f='index' ), [ ]),
        ] ),
    ]


if is_in_group( K_ROLE_DEVELOPER ):
    response.menu += [
        ( SPAN( T( 'Development' ),
                _class='dev_only' ),
          False,
          None, [ ( T( 'Configure' ), False, URL( c='config', f='index' ), []),
                  ( T( 'Company information' ),
                    (path_info == URL( request.application, 'company_info', 'edit' )),
                    URL( request.application, 'company_info', 'edit' ),
                    [] ),
                  ( T( 'User list' ),
                    URL() == URL( 'user_admin', 'list' ),
                    URL( 'user_admin', 'list' ),
                    [] ),
                  ( T( 'Pages' ),
                    (path_info == URL( request.application, 'page', 'index' )),
                    URL( request.application, 'page', 'index' ),
                    [] ),
                  ( T( 'Page blocks' ), False, URL( request.application, 'pageblock', 'index' ), [] ),
                  ( T( 'Blocks' ), False, URL( request.application, 'block', 'index' ), [] ),
                  ( T( 'Images' ), False, URL( request.application, 'images', 'index' ), [] ),
                  ( T( 'Image gallery' ),
                    URL() == URL( request.application, 'gallery', 'index' ),
                    URL( request.application, 'gallery', 'index' ),
                    [] ),
                  (T( 'Media gallery' ),
                   URL() == URL( request.application, 'media', 'list' ),
                   URL( request.application, 'media', 'list' ),
                   [ ]),
                  ( T( 'Categories' ), False, URL( request.application, 'category', 'index' ), [] ),
                  ( T( 'Mail queue' ), False, URL( request.application, 'mail_queue', 'index' ), [] ),
                  ( T( 'Web2py admin SEI' ),
                    False,
                    URL( a='admin', c='default', f='design', args=[ request.application ] ),
                    [] ),
                  ( T( 'User messages' ), True, URL( c='user_message', f='index' ), [] ),
                  ( T( 'View errors' ), True, URL( a='admin', c='default', f='errors',
                                                   args=[ request.application ] ), [] ),
                  ( T( 'View events' ),
                      (path_info == URL( c='auth_event_viewer', f='list' )),
                      URL( c='auth_event_viewer', f='list' ),
                      [] ),
        ]
          )
    ]

