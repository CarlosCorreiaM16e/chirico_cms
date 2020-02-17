# -*- coding: utf-8 -*-
from m16e import term, markmin_factory

if 0:
    import gluon
    from gluon.html import DIV
    from gluon.html import FORM
    from gluon.html import INPUT
    from gluon.html import TABLE
    from gluon.html import TD
    from gluon.html import TR
    from gluon.html import URL
    from gluon.dal import GQLDB, SQLDB
    from gluon.html import PRE, P, TAG, B
    from gluon.http import HTTP
    from gluon.sqlhtml import SQLFORM
    from gluon.validators import IS_NOT_EMPTY

    import gluon.languages.translator as T

    global auth; auth = gluon.tools.Auth()
    global cache; cache = gluon.cache.Cache()
    global crud; crud = gluon.tools.Crud()
    global db; db = gluon.sql.DAL()
    global request; request = gluon.globals.Request()
    global response; response = gluon.globals.Response()
    global service; service = gluon.tools.Service()
    global session; session = gluon.globals.Session()

    from gluon.http import redirect


def test_markmin():
    # s = '''
    # some text
    # [+[embed { 'class': 'text-center', 'tag': 'p' }:<iframe>some text display</iframe>]+]
    # more text
    # [+[embed {}:<iframe>more text display</iframe>]+]
    # still more text
    # '''
    # p = markmin_factory.parse_wt_embed( s )
    # term.printDebug( 'p: %s' % str( p ) )
    #
    # s = '''
    # some text
    # '''
    # s += markmin_factory.mk_wt_embed( '<iframe>some text display</iframe>',
    #                                   tag='div',
    #                                   css_class='text-center' )
    # s += '''
    # more text
    # '''
    # s += markmin_factory.mk_wt_embed( '<iframe>some text display</iframe>',
    #                                   tag='',
    #                                   css_class='' )
    # s += '''
    # still more text
    # '''

    # s = '''
    #  # Teste2                                                                                                                                                                                                                 +
    #                                                                                                                                                                                                               +
    # [+[embed{}:<iframe src="https://www.youtube.com/embed/U5_ZNDeYyuU" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen="" width="560" height="315" frameborder="0"></iframe>]+]
    # still more text
    # '''
    # p = markmin_factory.parse_wt_embed( s )
    s = '''
    <h1>teste</h1>
    <p>
        some text
    </p>
    <p>
        <iframe src="https://www.youtube.com/embed/U5_ZNDeYyuU" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen="" width="560" height="315" frameborder="0"></iframe>
    </p>
    '''
    p = markmin_factory.from_html( s )
    term.printDebug( 'p: %s' % str( p ) )



test_markmin()
