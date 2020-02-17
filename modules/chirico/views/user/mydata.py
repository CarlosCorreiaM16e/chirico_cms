# -*- coding: utf-8 -*-
import sys
import traceback

from belmiro.app import app_factory
from belmiro.app.ents import ent_factory
from belmiro.views.ents.edit import EntsEditView
from belmiro.views.ents.update import EntsUpdateView
from gluon import current, SPAN, SQLFORM, URL, SCRIPT, DIV, IS_IN_SET
from m16e import term, htmlcommon
from m16e.db import db_tables
from m16e.db.database import DbBaseTable

MAX_ZIP_HELPER_ROWS = 50


class CmsUserMydataView( EntsUpdateView ):
    controller_name = 'user'
    function_name = 'mydata'

    def __init__( self, db ):
        super( CmsUserMydataView, self ).__init__( db )
        self.table_model = db_tables.get_table_model( 'ent', db=db )
        self.fld_prefix = ''

    def do_process( self ):
        return super( CmsUserMydataView, self ).do_process()


    def fetch_record_id( self ):
        auth = current.auth
        db = self.db
        q_sql = (db.ent.auth_user_id == auth.user.id)
        self.record = self.table_model.select( q_sql ).first()
        if not self.record:
            auth = current.auth
            self.record_id = self.table_model.insert( dict( name=auth.user.first_name,
                                                            auth_user_id=auth.user.id,
                                                            email_1=auth.user.email ) )
            self.record = self.table_model[ self.record_id ]
        self.record_id = self.record.id


    def fetch_vars( self ):
        super( EntsEditView, self ).fetch_vars()


    def get_form_fields( self ):
        self.form_fields = [ 'name',
                             'email_1',
                             'nif',
                             'address_1',
                             'address_2',
                             'zip_code',
                             'country_id',
                             'phone_1',
                             'phone_2',
                             'url' ]
        return self.form_fields


    # def fetch_record( self, fetch_id=False ):
    #     super( CmsUserMydataView, self ).fetch_record( fetch_id )
    #     if not self.record:
    #         auth = current.auth
    #         self.record_id = self.table_model.insert( dict( name=auth.user.first_name,
    #                                                         auth_user_id=auth.user.id,
    #                                                         email_1=auth.user.email ) )
    #         super( CmsUserMydataView, self ).fetch_record( fetch_id=fetch_id )


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
        db = self.db
        auth = current.auth
        if form_fields is None:         form_fields = self.get_form_fields()
        if form_validators is None:     form_validators = self.get_form_validators()
        if deletable is None:           deletable = self.deletable
        if textarea_rows is None:       textarea_rows = self.textarea_rows
        if readonly_fields is None:     readonly_fields = self.get_readonly_fields()
        if exclude_fields is None:      exclude_fields = self.get_exclude_fields()
        if upload is None:              upload = self.upload
        if showid is None:              showid = self.showid
        if buttons is None:             buttons = self.buttons
        if extra_fields is None:        extra_fields = self.get_form_extra_fields()

        term.printDebug( 'exclude_fields: %s' % repr( exclude_fields ) )
        if form_fields:
            form_fields = [ f for f in form_fields
                            if f not in exclude_fields ]
        term.printDebug( 'form_fields: %s' % repr( form_fields ) )

        if self.table_model and isinstance( self.table_model, DbBaseTable ) and not form_fields:
            form_fields = [ f for f in db[ self.get_table_name() ].fields
                            if f not in exclude_fields ]

        table = self.get_db_table()
        if self.table_model:
            dv_list = self.table_model.get_default_attribute( 'validators' )
            for field, value in dv_list.items():
                table[ field ].requires = value
        #         term.printDebug( 'form_validators: %s' % repr( form_validators ) )
        for field, value in form_validators.items():
            table[ field ].requires = value
        record = None
        if self.record_id:
            table_model = self.get_db_table()
            record = table_model[ self.record_id ]
            record.name = auth.user.first_name
            record.email_1 = auth.user.email
        form = SQLFORM( table,
                        record,
                        fields=form_fields,
                        deletable=deletable,
                        upload=upload,
                        showid=showid,
                        buttons=buttons,
                        extra_fields=extra_fields )
        if form_id:
            form[ '_id' ] = form_id
        #         term.printDebug( 'form: %s' % form.xml() )
        from m16e.ui import ui_factory
        use_bootstrap_select = ui_factory.use_bootstrap_select()
        if use_bootstrap_select:
            for el in form.elements( 'select' ):
                # term.printDebug( 'el: %s' % repr( el ) )
                if len( el.components ) > htmlcommon.BOOTSTRAP_SELECTED_AUTO_THRESHOLD:
                    el[ '_data-none-selected-text' ] = htmlcommon.BOOTSTRAP_NONE_SELECTED_TEXT
                    el[ '_data-live-search' ] = 'true'
        if textarea_rows:
            for el in form.elements( 'textarea' ):
                el[ '_rows' ] = textarea_rows
        for f in readonly_fields:
            fld_id = '#%s_%s' % (self.table_model.table_name, f)
            el = form.element( fld_id )
            if el:
                if el.tag == 'select' or el[ '_type' ] == 'checkbox':
                    el[ '_disabled' ] = 'disabled'
                else:
                    el[ '_readonly' ] = 'readonly'
            #                 term.printDebug( 'el: %s' % el.xml() )
            else:
                term.printLog( 'el id not in form: %s' % fld_id )
        pp_vars = self.get_pre_populated_vars()
        for pp in pp_vars:
            form.vars[ pp ] = pp_vars[ pp ]

        if not self.record_id:
            d_values = self.get_default_values()
            if d_values:
                for k in d_values:
                    form.vars[ k ] = d_values[ k ]
        table_name = self.get_table_name()
        placeholders = self.get_form_fields_placeholders()
        #         term.printDebug( 'placeholders: %s' % repr( placeholders ) )
        for ph in placeholders:
            # term.printDebug( 'placeholders[ %s ]: %s' % (ph, placeholders[ ph ]) )
            el = form.element( '#%s_%s' % (table_name, ph) )
            if el:
                el[ '_placeholder' ] = placeholders[ ph ]
            else:
                raise Exception( 'element not found: #%s_%s' % (table_name, ph) )

        # term.printDebug( 'form: %s' % form.xml() )
        self.append_org_fields( form )

        # marker = SPAN( ' *', _class='not_empty' )
        url = URL( c=self.controller_name,
                   f='ajax_zip_code_changed' )
        onblur = '''
                    ajax( '%(url)s', [ 'zip_code' ], ':eval' );
                ''' % { 'url': url }
        el = form.element( '#ent_zip_code' )
        el[ '_onblur' ] = onblur
        if textarea_rows:
            for el in form.elements( 'textarea' ):
                el[ '_rows' ] = textarea_rows
        for f in readonly_fields:
            fld_id = '#%s_%s' % (self.table_model.table_name, f)
            el = form.element( fld_id )
            if el:
                if el[ '_type' ] == 'checkbox':
                    el[ '_disabled' ] = 'disabled'
                else:
                    el[ '_readonly' ] = 'readonly'
            #                 term.printDebug( 'el: %s' % el.xml() )
            else:
                term.printLog( 'el id not in form: %s' % fld_id )
        el = form.element( '#ent_nif' )
        el[ '_onchange' ] = '''ajax( '%s', [ 'country_id', 'nif' ], ':eval' )''' \
            % URL( c=self.controller_name, f='ajax_validate_nif' )
        #         term.printDebug( 'form: %s' % repr( form ) )
        return form


    def set_auto_fields( self, upd ):
        db = self.db
        term.printDebug( 'upd: %s' % repr( upd ) )
        if not upd.country_id:
            upd.country_id = self.record.country_id
        if 'zip_code' in upd or not self.record.city:
            if not 'zip_code' in upd:
                upd.zip_code = self.record.zip_code
            data = ent_factory.get_address_tax_data_from_zip( upd.country_id,
                                                              upd.zip_code,
                                                              db=db )
            if data._errors:
                self.set_result( message=data._errors )
                return upd

            for f in data:
                upd[f] = data[f]
        term.printDebug( 'upd: %s' % repr( upd ), print_trace=True )


    def pre_ins( self, upd ):
        super( CmsUserMydataView, self ).pre_ins( upd )
        self.set_auto_fields( upd )


    def pre_upd( self, upd ):
        super( CmsUserMydataView, self ).pre_upd( upd )
        self.set_auto_fields( upd )


    def update_record( self, upd ):
        super( CmsUserMydataView, self ).update_record( upd )
        db = self.db
        user = {}
        if 'name' in upd:
            user[ 'first_name' ] = upd.name
        if 'email_1' in upd:
            user[ 'email' ] = upd.email_1
        if user:
            db( db.auth_user.id == self.record.auth_user_id).update( **user )


    def get_unfilled_user_fields( self ):
        db = current.db
        fld_list = []
        e_fields = [ 'address_1',
                     'zip_code',
                     'nif',
                     'country_id',
                     'phone_1' ]
        #     term.printDebug( 'gp: %s' % repr( gp ) )
        for f in e_fields:
            if not self.record[ f ]:
                fld_list.append( f )
        return fld_list


    def process_form( self, form ):
        super( EntsEditView, self ).process_form( form )


    def post_process_form( self, form ):
        super( CmsUserMydataView, self ).post_process_form( form )
        db = self.db
        auth = current.auth
        c_model = db_tables.get_table_model( 'county', db=db )
        d_model = db_tables.get_table_model( 'district', db=db )
        ent_city = ''
        ent_district_name = ''
        ent_county_name = ''
        if self.record.city:
            ent_city = self.record.city
        if self.record.district_id:
            district = d_model[ self.record.district_id ]
            ent_district_name = district.name if district else ''
        if self.record.county_id:
            county = c_model[ self.record.county_id ]
            ent_county_name = county.name if county else ''
        unfilled_list = self.get_unfilled_user_fields()
        self.set_result( data=dict( form=form,
                                    jscript=self.get_zip_code_helper(),
                                    ent_city=ent_city,
                                    ent_district_name=ent_district_name,
                                    ent_county_name=ent_county_name,
                                    unfilled_list=unfilled_list ) )


    def get_zip_code_helper( self ):
        url = URL( c=self.controller_name,
                   f='ajax_zip_code_helper' )
        js = SCRIPT( '''
            jQuery( document ).ready( function() {
                jQuery( '#ent_zip_code' ).attr( 'autocomplete','off' );
            } );
            jQuery( '#ent_zip_code' ).keyup( function( e ) {
                if( e.keyCode == 27 ) {
                    jQuery( '#%(helper)s' ).hide();
                }
                else {
                    jQuery( '#%(helper)s' ).show();
                }
                ajax( '%(url)s', [ 'zip_code' ], '%(helper)s' );
            } );
            ''' % { 'url': url,
                    'helper': 'zip_code_helper' } )
        # term.printDebug( 'js: %s' % js )
        return js


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
                    term.printDebug( 'czc: %s' % repr( czc ) )
                    onclick = '''
                        window.console && console.log( 'zip: ' + '%(zip_part_1)s-%(zip_part_2)s' );
                        jQuery( '#ent_zip_code' ).removeAttr( 'onblur' );
                        jQuery( '#ent_zip_code' ).val( '%(zip_part_1)s-%(zip_part_2)s' );
                        jQuery( '#ent_city' ).html( '%(zip_city)s' );
                        jQuery( '#ent_county_name' ).html( '%(county_name)s' );
                        jQuery( '#ent_district_name' ).html( '%(district_name)s' );
                        jQuery( '#%(helper)s' ).empty();
                    ''' % czc
                    term.printDebug( 'onclick: %s' % repr( onclick ) )

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
                        jQuery( '#ent_city' ).html( '%(zip_city)s' );
                        jQuery( '#ent_county_name' ).html( '%(county_name)s' );
                        jQuery( '#ent_district_name' ).html( '%(district_name)s' );
                        jQuery( '#%(helper)s' ).empty();
                    ''' % czc
                    term.printDebug( 'js: %s' % ( js ) )
                    return js
        except:
            t, v, tb = sys.exc_info()
            traceback.print_exception( t, v, tb )
        return ''


    def ajax_validate_nif( self ):
        request = current.request
        T = current.T
        term.printLog( 'request.args: %s' % repr( request.args ) )
        term.printLog( 'request.vars: %s' % repr( request.vars ) )
        try:
            nif = request.vars.nif
            country_id = int( request.vars.country_id )
            valid = ent_factory.is_valid_nif( country_id, nif )
            jq = '''
                jQuery( '#nif__error' ).remove();
            '''
            if not valid:
                term.printLog( 'invalid nif: %s' % nif )
                jq += '''
                    jQuery( '#ent_nif' ).parent().append(
                        '<div class="error" id="nif__error">%s</div>' );
                ''' % ( T( 'Invalid NIF for portuguese companies' ) )
            term.printDebug( 'valid: %s' % repr( valid ) )
            return jq
        except:
            t, v, tb = sys.exc_info()
            traceback.print_exception( t, v, tb )
        return ''


