# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
from belmiro.app import app_factory
from m16e.system import login

if 0:
    import gluon
    global auth; auth = gluon.tools.Auth()
    global cache; cache = gluon.cache.Cache()
    global crud; crud = gluon.tools.Crud()
    global db; db = gluon.DAL()
    global request; request = gluon.globals.Request()
    global response; response = gluon.globals.Response()
    global service; service = gluon.tools.Service()
    global session; session = gluon.globals.Session()
    from gluon import redirect
    from gluon.html import URL


#------------------------------------------------------------------
@auth.requires_login()
def index():
    """
    """
    ci = app_factory.get_company_info_data( db=db )
    return dict( ci=ci )


@auth.requires_login()
def support():
    """
    """
    ci = app_factory.get_company_info_data( db=db )
    next_url = URL( a='clientes',
                    c='support',
                    f=request.args( 0 ),
                    vars={ 'fiscal_id': ci.company_tax_id } )

    url = login.prepare_user_login( 'clientes',
                                next_url=next_url )
    redirect( url )


@auth.requires_login()
def service_conditions():
    """
    """
    ci = app_factory.get_company_info_data( db=db )
    return dict( ci=ci )

