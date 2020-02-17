# -*- coding: utf-8 -*-
from app import db_sets
from gluon import current, DIV, SPAN, URL
from m16e import htmlcommon
from m16e.kommon import KDT_SELECT_INT, KDT_SELECT_CHAR, KDT_FILE, KDT_BOOLEAN
from m16e.ktfact import KTF_AJAX_FIELD_CHANGED


class ListFilterCondition( object ):
    def __init__( self,
                  list_filter,
                  condition_expression=None,
                  db=None ):
        """

        Args:
            list_filter: ListFilter
            condition_expression: ConditionExpression
            db:
        """
        if not db:
            db = current.db
        self.db = db
        self.list_filter= list_filter
        self.condition_expression = condition_expression


    def get_condition_row( self, row_id ):
        cr_div = DIV( _class='row' )
        cr_div.append( DIV( self.__get_el_l_par( row_id ),
                            _class='col-md-1' ) )
        cr_div.append( DIV( self.__get_el_field( row_id ),
                            _class='col-md-3' ) )
        cr_div.append( DIV( self.__get_el_test_op( row_id ),
                            _class='col-md-1' ) )
        cr_div.append( DIV( self.__get_el_value( row_id ),
                            _class='col-md-3' ) )
        cr_div.append( DIV( self.__get_el_r_par( row_id ),
                            _class='col-md-1' ) )
        cr_div.append( DIV( self.__get_el_next_op( row_id ),
                            _class='col-md-1' ) )
        cr_div.append( DIV( self.__get_el_del_bt( row_id ),
                            _class='col-md-2' ) )
        return cr_div


    def get_onchange_js( self, fld_id ):
        onchange = '''
            ajax( '%(url)s', [ '%(fld)s' ], ':eval' );
            ''' % { 'url': URL( c=self.list_filter.plastic_view.controller_name,
                                f=KTF_AJAX_FIELD_CHANGED ),
                    'fld': fld_id }
        return onchange


    def __get_el_l_par( self, row_id ):
        fld_name = 'l_par'
        value = self.condition_expression.l_par or 0
        inp = htmlcommon.get_input_field( '%s_%s' % (row_id, fld_name),
                                          value='(' * value,
                                          input_id='%s_%s' % (row_id, fld_name),
                                          css_style='width: 3em;' )
        return inp

    def __get_el_r_par( self, row_id ):
        fld_name = 'r_par'
        value = self.condition_expression.r_par or 0
        inp = htmlcommon.get_input_field( '%s_%s' % (row_id, fld_name),
                                          value=')' * value,
                                          input_id='%s_%s' % (row_id, fld_name),
                                          css_style='width: 3em;' )
        return inp

    def __get_el_field( self, row_id ):
        fld_name = 'fld_name'
        fld_id = '%s_%s' % (row_id, fld_name)
        # term.printDebug( 'row_id: %s; values: %s' % ( repr( row_id ), repr( values ) ) )
        fld_list = self.list_filter.get_query_fields()
        q_options = [ ('', '')]
        for fld in fld_list:
            q_options.append( (fld, fld_list[ fld ].title) )
        on_change = self.get_onchange_js( fld_id )
        sel = htmlcommon.get_selection_field( fld_id,
                                              input_id=fld_id,
                                              options=q_options,
                                              selected=self.condition_expression.value,
                                              on_change=on_change,
                                              css_class='generic-widget form-control',
                                              css_style='max-width: 200px;' )
        return sel

    def __get_el_test_op( self, row_id ):
        fld_name = 'test_op'
        fld_id = '%s_%s' % (row_id, fld_name)
        sel = htmlcommon.get_selection_field( fld_id,
                                              input_id=fld_id,
                                              options=db_sets.TEST_OP_LIST,
                                              selected=self.condition_expression.test_op,
                                              css_class='generic-widget form-control' )
        return sel

    def __get_el_value( self, row_id ):
        fld_name = 'value'
        fld_id = '%s_%s' % (row_id, fld_name)
        fld_type = self.condition_expression.condition_field.fld_type
        if fld_type in (KDT_SELECT_INT, KDT_SELECT_CHAR):
            on_change = self.get_onchange_js(fld_id)
            el = htmlcommon.get_selection_field( fld_id,
                                                 input_id=fld_id,
                                                 options=self.condition_expression.condition_field.fld_options,
                                                 selected=self.condition_expression.value,
                                                 on_change=on_change,
                                                 css_class='generic-widget form-control',
                                                 css_style='max-width: 200px;')
        else:
            if fld_type == KDT_FILE:
                col_type = 'file'
            elif fld_type == KDT_BOOLEAN:
                col_type = 'checkbox'
            else:
                col_type = 'text'
            # term.printDebug( 'opvars[%s]: %s' % ( varname, repr( opvars[ varname ] ) ) )
            el = htmlcommon.get_input_field( fld_id,
                                             value=self.condition_expression.value,
                                             input_type=col_type,
                                             input_id=fld_id,
                                             css_class='small',
                                             value_type=fld_type )

        return el

    def __get_el_next_op( self, row_id ):
        fld_name = 'next_op'
        fld_id = '%s_%s' % (row_id, fld_name)
        options = db_sets.TEST_BOOL_LIST[:]
        options.insert( 0, ('', '') )
        on_change = None
        on_change = self.get_onchange_js( fld_id )
        sel = htmlcommon.get_selection_field( fld_id,
                                              input_id=fld_id,
                                              options=options,
                                              selected=self.condition_expression.next_op,
                                              css_class='generic-widget form-control',
                                              on_change=on_change )
        return sel

    def __get_el_del_bt( self, row_id ):
        fld_id = '%s_del' % (row_id)

        span = SPAN( _id=fld_id,
                     _class='dark_bg hidden' )
        return span

