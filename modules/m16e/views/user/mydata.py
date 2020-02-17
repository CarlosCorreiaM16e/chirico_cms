# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

import sys
import traceback

from app import db_sets
from gluon import current, IS_NULL_OR
from gluon.dal import Field
from gluon.html import URL, DIV, A, SCRIPT, SPAN
from gluon.sqlhtml import SQLFORM
from gluon.storage import Storage
from gluon.validators import IS_IN_SET, IS_DATE
from m16e import term
from m16e.db import db_tables
from m16e.i18n.pt_pt.widgets import nif_validator, zip_validator
from m16e.user_factory import is_in_group
from m16e.views.edit_base_view import BaseFormView


MAX_ZIP_HELPER_ROWS = 50


class UserMydataView( BaseFormView ):
    controller_name = 'user'
    function_name = 'mydata'


    def __init__( self, db ):
        super( UserMydataView, self ).__init__( db )


    def do_process( self ):
        return super( UserMydataView, self ).do_process()


    def get_form( self,
                  form_fields=None,
                  form_validators=None,
                  deletable=None,
                  textarea_rows=None,
                  readonly_fields=None,
                  exclude_fields=None,
                  upload=None,
                  showid=None,
                  buttons=None,
                  extra_fields=None,
                  form_id=None ):
        if readonly_fields is None:
            readonly_fields = []
#         term.printDebug( 'db_record: %s' % repr( db_record ) )
#         term.printDebug( 'self.table_model.db: %s' % repr( self.table_model.db ) )
#         term.printDebug( 'self.table_model.table_name: %s' % repr( self.table_model.table_name ) )
        T = current.T
        session = current.session
        auth = session.auth
        db = self.db
        if not form_fields:
            gp_model = db_tables.get_table_model( 'global_panel', db=db )
            q_sql = (db.global_panel.auth_user_id == auth.user.id)
            gp = gp_model.select( q_sql ).first()
            auth_user = db.auth_user[ auth.user.id ]
            term.printDebug( 'auth_user: %s' % (repr( auth_user ) ) )
            marker = SPAN( ' *', _class='not_empty')
            form_fields = []
            form_fields.append( Field( 'auth_user_id',
                                       'int',
                                       writable=False,
                                       default=auth_user.id ) )
            form_fields.append( Field( 'first_name',
                                       length=128,
                                       notnull=True,
                                       writable=False,
                                       label=T( 'Full name' ),
                                       default=auth_user.first_name ) )
            form_fields.append( Field( 'email',
                                       length=128,
                                       unique=True,
                                       writable=False,
                                       notnull=True,
                                       default=auth_user.email ) )
            form_fields.append( Field( 'address_1',
                                       'string',
                                       label=T( 'Address #1' ),
                                       notnull=True,
                                       default=gp.address_1 ) )
            form_fields.append( Field( 'address_2',
                                       'string',
                                       label=T( 'Address #2' ),
                                       default=gp.address_2 ) )
            form_fields.append( Field( 'zip_code', 'string',
                                       label=T( 'Zip code' ),
                                       requires=zip_validator.is_valid_zip(),
                                       notnull=True,
                                       default=gp.zip_code ) )
            form_fields.append( Field( 'fiscal_id',
                                       'string_autocompletion',
                                       label=T( 'Fiscal Id.' ),
                                       requires=nif_validator.is_valid_nif(),
                                       unique=True,
                                       default=auth_user.fiscal_id ) )
            form_fields.append( Field( 'phone_1',
                                       'string',
                                       label=T( 'Mobile phone' ),
                                       notnull=True,
                                       default=gp.phone_1 ) )
            form_fields.append( Field( 'phone_2',
                                       'string',
                                       label=T( 'Other phone' ),
                                       default=gp.phone_2 ) )
            form_fields.append( Field( 'birth_date',
                                       'date_nopicker',
                                       label=T( 'Birth' ),
                                       notnull=True,
                                       requires=IS_DATE(),
                                       default=gp.birth_date ) )
            form_fields.append( Field( 'sex',
                                       'string',
                                       label=T( 'Sex' ),
                                       requires=IS_NULL_OR( IS_IN_SET( db_sets.GP_SEX_SET ) ),
                                       default=gp.sex ) )
            form_fields.append( Field( 'is_focus_group',
                                       'boolean',
                                       label=T( 'Focus groups' ),
                                       default=gp.is_focus_group ) )
            form_fields.append( Field( 'is_phone_survey',
                                       'boolean',
                                       label=T( 'Phone surveys' ),
                                       default=gp.is_phone_survey ) )

        form = SQLFORM.factory( *form_fields )
#         term.printDebug( 'table: %s' % repr( table ) )
#         term.printDebug( 'form_fields: %s' % repr( form_fields ) )
        url = URL( c=self.controller_name,
                   f='ajax_zip_code_changed' )
        onblur = '''
            ajax( '%(url)s', [ 'zip_code' ], ':eval' );
        ''' % { 'url': url }
        el = form.element( '#no_table_zip_code' )
        el[ '_onblur' ] = onblur
        if textarea_rows:
            for el in form.elements( 'textarea' ):
                el['_rows'] = textarea_rows
        for f in readonly_fields:
            fld_id = '#%s_%s' % ( self.table_model.table_name, f )
            el = form.element( fld_id )
            if el:
                if el[ '_type' ] == 'checkbox':
                    el['_disabled'] = 'disabled'
                else:
                    el['_readonly'] = 'readonly'
#                 term.printDebug( 'el: %s' % el.xml() )
            else:
                term.printLog( 'el id not in form: %s' % fld_id )
#         term.printDebug( 'form: %s' % repr( form ) )
        return form


    def upd_auth_user( self, form ):
        db = self.db
        upd = self.get_changed_fields( form, db_table=db.auth_user )
        if upd:
            db( db.auth_user.id == self.record.auth_user_id ).update( **upd )
        return upd


    def process_form_action( self, form ):
        term.printDebug( 'form.vars: ' + repr( form.vars ) )
        if self.action == self.submit_action:
            upd_au = self.upd_auth_user( form )
            if upd_au:
                msg = self.msg_record_updated
            else:
                msg = self.msg_nothing_to_update
            url = URL( c=self.controller_name,
                       f=self.function_name )
            self.set_result( redirect=url, message=msg )


    def post_process_form( self, form ):
        super( UserMydataView, self ).post_process_form( form )
        db = self.db
        T = current.T
        auth = current.auth
        c_model = db_tables.get_table_model( 'county', db=db )
        d_model = db_tables.get_table_model( 'district', db=db )
        s_model = db_tables.get_table_model( 'survey', db=db )
        sa_model = db_tables.get_table_model( 'survey_answer', db=db )
        sp_model = db_tables.get_table_model( 'survey_panel', db=db )
        is_dev = is_in_group( 'dev' )
        is_editor = is_in_group( 'editor' )

        gp_city = ''
        gp_district_name = ''
        gp_county_name = ''
        if self.record.city:
            gp_city = self.record.city
        if self.record.district_id:
            district = d_model[ self.record.district_id ]
            gp_district_name = district.name if district else ''
        if self.record.county_id:
            county = c_model[ self.record.county_id ]
            gp_county_name = county.name if county else ''

        self.set_result( data=dict( form=form,
                                    jscript=self.get_zip_code_helper(),
                                    is_dev=is_dev,
                                    is_editor=is_editor,
                                    gp_city=gp_city,
                                    gp_district_name=gp_district_name,
                                    gp_county_name=gp_county_name ) )


    def get_zip_code_helper( self ):
        url = URL( c=self.controller_name,
                   f='ajax_zip_code_helper' )
        js = SCRIPT( '''
            jQuery( document ).ready( function() {
                jQuery( '#no_table_zip_code' ).attr( 'autocomplete','off' );
            } );
            jQuery( '#no_table_zip_code' ).keyup( function( e ) {
                window.console && console.log( 'keyup (' + e.keyCode );
                if( e.keyCode == 27 ) {
                    jQuery( '#%(helper)s' ).hide();
                }
                else {
                    jQuery( '#%(helper)s' ).show();
                }
                window.console && console.log( 'keyup' );
                ajax( '%(url)s', [ 'zip_code' ], '%(helper)s' );
            } );
            ''' % { 'url': url,
                    'helper': 'zip_code_helper' } )
        # term.printDebug( 'js: %s' % js )
        return js

#     #------------------------------------------------------------------
#     def process( self ):
#         #------------------------------------------------------------------
#         request = current.request
#         response = current.response
#         session = current.session
#         T = current.T
#         db = self.db
#         auth = current.auth
#         redirect = None
#
#         term.printLog( 'request.args: ' + repr( request.args ) )
#         term.printLog( 'request.vars: ' + repr( request.vars ) )
#
#         # pcam = db_tables.get_table_model( 'panel_current_account', db=db )
#         sa_model = db_tables.get_table_model( 'survey_answer', db=db )
#         qam = db_tables.get_table_model( 'question_answer', db=db )
#         s_model = db_tables.get_table_model( 'survey', db=db )
#         gp_model = db_tables.get_table_model( 'global_panel', db=db )
#         sp_model = db_tables.get_table_model( 'survey_panel', db=db )
#         c_model = db_tables.get_table_model( 'county', db=db )
#         d_model = db_tables.get_table_model( 'district', db=db )
#
#         ac_model = db_tables.get_table_model( 'area_county', db=db )
#         ca_model = db_tables.get_table_model( 'country_area', db=db )
#         cz_model = db_tables.get_table_model( 'country_zone', db=db )
#
#         action = request.post_vars.action
#         if not action and request.vars.action:
#             action = request.vars.action
#         term.printLog( 'action: ' + repr( action ) )
#
#         term.printDebug( 'auth.user: %s' % repr( auth.user ) )
#         q_sql = (db.global_panel.auth_user_id == auth.user.id)
#         global_panel = gp_model.select( q_sql ).first()
#         if not global_panel:
#             message = 'User (%d: %s) not in global panel' % ( auth.user.id,
#                                                                   auth.user.email )
#             auth.log_event( message, origin='mydata' )
#             return self.set_result( redirect=URL( c='default', f='index' ),
#                                     message=T( 'An error has occurred' ) )
#
#         unfilled_list = global_panel_factory.get_unfilled_user_fields( auth.user.id )
#         term.printDebug( 'unfilled_list: %s' % repr( unfilled_list ) )
#         main_survey = Storage()
#         # global_panel_factory.check_first_login()
#         if not unfilled_list:
#             q_sql = (db.survey.is_main == True)
#             main_survey.survey = s_model.select( q_sql ).first()
#             term.printDebug( 'main_survey.survey: %s' % repr( main_survey.survey ) )
#             q_sql = (db.survey_panel.survey_id == main_survey.survey.id)
#             q_sql &= (db.survey_panel.global_panel_id == global_panel.id)
#             sp = sp_model.select( q_sql ).first()
#             if not sp:
#                 term.printDebug( 'failed to find in survey_panel: (survey: %s; global_panel: %s'
#                                  % ( repr( main_survey.survey.id ),
#                                      repr( global_panel.id ) ) )
#             else:
#                 q_sql = (db.survey_answer.survey_panel_id == sp.id)
#                 main_survey.survey_answer = sa_model.select( q_sql,
#                                                              print_query=True ).first()
#                 term.printDebug( 'main_survey.survey_answer: %s' % repr( main_survey.survey_answer ) )
# #             if not main_survey.survey_answer:
# #                 return Storage( dict=dict(),
# #                                 redirect=URL( c='survey_filler',
# #                                               f='index',
# #                                               args=[ main_survey.survey.id ] ) )
#
# #         db_tables.get_table_model( 'survey_user_data_dict' )
#         form = self.get_form()
#         if form.accepts( request.vars, session, dbio = False ):
#             term.printLog( 'form.vars: ' + repr( form.vars ) )
#             if action == ACT_SUBMIT:
#                 changed = False
#                 upd = htmlcommon.getChangedFields( form.vars,
#                                                    request.post_vars,
#                                                    db.global_panel )
#                 if upd:
#                     term.printDebug( 'upd: %s' % ( repr( upd ) ) )
#                     changed = True
#                     z_validator = zip_validator.is_valid_zip()
#                     if 'zip_code' in upd:
#                         zc = upd[ 'zip_code' ]
#                         czc = z_validator.get_county_zip_code( zc )
#                         upd.city = czc.zip_city
#                         upd.county_id = czc.county_id
#                         county = c_model[ czc.county_id ]
#                         upd.district_id = county.district_id
#                         c = c_model[ czc.county_id ]
#                         q_sql = (db.area_county.county_id == czc.county_id)
#                         ac = ac_model.select( q_sql ).first()
#                         ca = ca_model[ ac.country_area_id ]
#                         cz = cz_model[ ca.country_zone_id ]
#                         upd.country_area_id = ca.id
#                         upd.country_zone_id = cz.id
#                         upd.country_region_id = cz.country_region_id
#                     self.table_model.update_by_id( global_panel.id,
#                                                    upd,
#                                                    print_query=True )
#                     if 'birth_date' in upd:
#                         global_panel = gp_model[ global_panel.id ]
#                         global_panel_factory.recalc_age_group( global_panel )
#
#                     response.flash = T( 'Record updated' )
#                 else:
#                     response.flash = T( 'Nothing changed' )
#                 upd = htmlcommon.getChangedFields( form.vars,
#                                                    request.post_vars,
#                                                    db.auth_user )
#                 if upd:
#                     term.printDebug( 'upd: %s' % ( repr( upd ) ) )
#                     changed = True
#                     db( db.auth_user.id == global_panel.auth_user_id).update( **upd )
#                     session.flash = T( 'Record updated' )
#                     return Storage( dict=dict(),
#                                     redirect=URL( c='user', f='mydata' ) )
#                 elif not changed:
#                     response.flash = T( 'Nothing changed' )
#
#         elif form.errors:
#             term.printLog( 'errors: %s' % ( repr( form.errors ) ) )
#             response.flash = T( 'Form has errors' )
#
#         # term.printDebug( 'global_panel: ' + repr( global_panel ) )
#         cc_list = current_account_factory.get_current_account_last_rows( global_panel.id, 5 )
#         for cc in cc_list:
#             cc.status_str = db_sets.CA_STATUS_SET[  cc.present_status ]
#             term.printDebug( 'cc: ' + repr( cc ) )
#         ac_model = db_tables.get_table_model( 'app_config', db=db )
#         ac = ac_model[ 1 ]
#         # term.printDebug( 'ac: ' + repr( ac ) )
#         req_credits_link = ''
#         if cc_list:
#             term.printDebug( 'cc[-1]: ' + repr( cc_list[-1] ) )
#             # if ac.credits_pay_threshold <= cc_list[ -1 ].balance:
#             req_credits_link = A( T( 'See detail' ),
#                                   _href=URL( c='current_account',
#                                              f='list',
#                                              vars={ KQV_GLOBAL_PANEL_ID: global_panel.id } ),
#                                   _class='btn btn-info' )
#         term.printDebug( 'req_credits_link: ' + repr( req_credits_link ) )
#         # term.printDebug( 'main_survey.survey: %s\n\n' % repr( main_survey.survey ) )
# #         term.printDebug( 'main_survey.survey_answer: %s' % repr( main_survey.survey_answer ) )
#         is_dev = is_in_group( 'dev' )
#         is_editor = is_in_group( 'editor' )
#
#         gp_city = ''
#         gp_district_name = ''
#         gp_county_name = ''
#         if global_panel.city:
#             gp_city = global_panel.city
#         if global_panel.district_id:
#             district = d_model[ global_panel.district_id ]
#             gp_district_name = district.name if district else ''
#         if global_panel.county_id:
#             county = c_model[ global_panel.county_id ]
#             gp_county_name = county.name if county else ''
#
#         current_surveys = []
#         is_interviewer = is_in_group( 'interviewer' )
#         is_panel = is_in_group( 'panel' )
#         if is_interviewer:
#             si_model = db_tables.get_table_model( 'survey_interviewer', db=db )
#             q_sql = (db.survey_interviewer.global_panel_id == global_panel.id)
#             rows = si_model.select( q_sql, orderby='survey_id' )
#             for r in rows:
#                 survey = s_model[ r.survey_id ]
#                 current_surveys.append( Storage( survey_id=r.survey_id,
#                                                  survey_name=survey.name ) )
#
#         return Storage( dict=dict( form=form,
#                                    jscript=self.get_zip_code_helper(),
#                                    is_dev=is_dev,
#                                    is_editor=is_editor,
#                                    is_panel=is_panel,
#                                    is_interviewer=is_interviewer,
#                                    global_panel=global_panel,
# #                                    survey_list=survey_list,
#                                    cc_list=cc_list,
#                                    req_credits_link=req_credits_link,
#                                    unfilled_list=unfilled_list,
#                                    main_survey=main_survey,
#                                    gp_city=gp_city,
#                                    gp_district_name=gp_district_name,
#                                    gp_county_name=gp_county_name,
#                                    current_surveys=current_surveys ),
#                         redirect=redirect )

    #----------------------------------------------------------------------
    def ajax_zip_code_helper( self ):
        '''
        args=[]
        '''
        request = current.request
        T = current.T
        db = self.db

        term.printLog( 'request.args: %s\n' % ( repr( request.args ) ) )
        term.printLog( 'request.vars: %s\n' % ( repr( request.vars ) ) )
        try:
            if request.vars.zip_code:
                czc_model = db_tables.get_table_model( 'county_zip_code', db=db )
                c_model = db_tables.get_table_model( 'county', db=db )
                d_model = db_tables.get_table_model( 'district', db=db )
                z_parts = request.vars.zip_code.split( '-' )
                zp1 = z_parts[0].strip()
                if len( zp1 ) < 4:
                    zp1 += '%'
                zp2 = z_parts[1].strip() if len( z_parts ) > 1 else None
                q_sql = (db.county_zip_code.zip_part_1.like( zp1 ))
                if zp2:
                    if len( zp2 ) < 3:
                        zp2 += '%'
                    q_sql &= (db.county_zip_code.zip_part_2.like( zp2[:3] ))
                czc_list = czc_model.select( q_sql,
                                             limit=MAX_ZIP_HELPER_ROWS,
                                             orderby='zip_part_1, zip_part_2' )
                # term.printDebug( 'sql: %s' % ( db._lastsql ) )

                div = DIV( _style='z-index: 2000' )
                for czc in czc_list:
                    zc_row = '%s-%s %s' % ( czc.zip_part_1,
                                            czc.zip_part_2,
                                            czc.zip_city )
                    czc.helper = 'zip_code_helper'
                    county = c_model[ czc.county_id ]
                    czc.county_name = county.name
                    czc.district_name = d_model[ county.district_id ].name
                    onclick = '''
                        jQuery( '#no_table_zip_code' ).removeAttr( 'onblur' );
                        jQuery( '#no_table_zip_code' ).val( '%(zip_part_1)s-%(zip_part_2)s' );
                        jQuery( '#gp_city' ).html( '%(zip_city)s' );
                        jQuery( '#gp_county_name' ).html( '%(county_name)s' );
                        jQuery( '#gp_district_name' ).html( '%(district_name)s' );
                        jQuery( '#%(helper)s' ).empty();
                    ''' % czc

                    div1 = DIV( zc_row,
                                _onclick=onclick,
                                _onmouseover="this.style.backgroundColor='#ffeeff'",
                                _onmouseout="this.style.backgroundColor='#ffffff'" )
                    div.append( div1 )
                    term.printDebug( 'name: %s' % ( zc_row ) )
                    term.printDebug( 'onclick: %s' % ( onclick ) )

                term.printDebug( 'div: %s' % ( div.xml() ) )
                return div
        except:
            t, v, tb = sys.exc_info()
            traceback.print_exception( t, v, tb )
        return ''

    #----------------------------------------------------------------------
    def ajax_zip_code_changed( self ):
        '''
        args=[]
        '''
        request = current.request
        T = current.T
        db = self.db

        term.printLog( 'request.args: %s\n' % ( repr( request.args ) ) )
        term.printLog( 'request.vars: %s\n' % ( repr( request.vars ) ) )
        try:
            if request.vars.zip_code:
                czc_model = db_tables.get_table_model( 'county_zip_code', db=db )
                c_model = db_tables.get_table_model( 'county', db=db )
                d_model = db_tables.get_table_model( 'district', db=db )
                z_parts = request.vars.zip_code.split( '-' )
                zp1 = z_parts[0].strip()
                if len( zp1 ) < 4:
                    zp1 += '%'
                zp2 = z_parts[1].strip() if len( z_parts ) > 1 else None
                q_sql = (db.county_zip_code.zip_part_1.like( zp1 ))
                if zp2:
                    if len( zp2 ) < 3:
                        zp2 += '%'
                    q_sql &= (db.county_zip_code.zip_part_2.like( zp2[:3] ))

                    czc = czc_model.select( q_sql ).first()
                    # term.printDebug( 'sql: %s' % ( db._lastsql ) )
                    county = c_model[ czc.county_id ]
                    czc.county_name = county.name
                    czc.district_name = d_model[ county.district_id ].name
                    czc.helper = 'zip_code_helper'
                    js = '''
                        jQuery( '#gp_city' ).html( '%(zip_city)s' );
                        jQuery( '#gp_county_name' ).html( '%(county_name)s' );
                        jQuery( '#gp_district_name' ).html( '%(district_name)s' );
                        jQuery( '#%(helper)s' ).empty();
                    ''' % czc
                    term.printDebug( 'js: %s' % ( js ) )
                    return js
        except:
            t, v, tb = sys.exc_info()
            traceback.print_exception( t, v, tb )
        return ''



