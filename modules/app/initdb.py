# -*- coding: utf-8 -*-
from getpass import getpass

from app import db_sets
from gluon import current
from m16e.db.database import table_exists, index_exists, column_exists, constraint_exists, sequence_exists, \
    fetch_record_by_id
from m16e.kommon import DT

db = current.db


def init_app_theme():
    if not table_exists( 'app_theme', db=db ):
        sql = '''
            CREATE TABLE app_theme (
                id SERIAL PRIMARY KEY,
                name CHARACTER VARYING(32) NOT NULL,
                title CHARACTER VARYING(1024) NOT NULL,
                subtitle CHARACTER VARYING(1024) NOT NULL,
                logo_header CHARACTER VARYING(1024) NOT NULL,
                login_button_position CHARACTER VARYING(512) NOT NULL,
                meta_name CHARACTER VARYING(1024),
                stylesheet CHARACTER VARYING(1024)
            )
        '''
        db.executesql( sql )


def init_unit_type():
    if not table_exists( 'unit_type', db=db ):
        sql = '''
            CREATE TABLE unit_type (
                id SERIAL PRIMARY KEY,
                name CHARACTER VARYING(128) NOT NULL,
                path CHARACTER VARYING(512) NOT NULL,
                parent_unit_type_id INTEGER,
                preferred_order INTEGER DEFAULT 1,
                meta_name CHARACTER VARYING(128) NOT NULL
            )
        '''
        db.executesql( sql )


def init_company_info():
    if not table_exists( 'company_info', db=db ):
        sql = '''
            CREATE TABLE company_info (
                id SERIAL PRIMARY KEY,
                mail_smtp_server CHARACTER VARYING(512),
                mail_account CHARACTER VARYING(512),
                mail_user CHARACTER VARYING(512),
                mail_password CHARACTER VARYING(512),
                mail_default_cc CHARACTER VARYING(512),
                mail_default_bcc CHARACTER VARYING(512),
                mail_default_sign CHARACTER VARYING(512),
                mail_smtp_server_port CHARACTER VARYING(8),
                mail_tls boolean,
                company_name CHARACTER VARYING(512),
                company_tax_id CHARACTER VARYING(32),
                company_address CHARACTER VARYING(512),
                company_city CHARACTER VARYING(128),
                company_postal_code CHARACTER VARYING(32),
                company_country CHARACTER VARYING(256),
                company_phone CHARACTER VARYING(32),
                company_fax CHARACTER VARYING(32),
                company_email CHARACTER VARYING(256),
                company_website CHARACTER VARYING(512),
                company_country_iso3166 CHARACTER VARYING(8)
            )
        '''
        db.executesql( sql )


def init_long_task():
    if not table_exists( 'long_task', db=db ):
        sql = '''
            CREATE TABLE long_task (
                id SERIAL PRIMARY KEY,
                task_name CHARACTER VARYING(256),
                force_single_instance boolean DEFAULT true NOT NULL
            )
        '''
        db.executesql( sql )


def init_thread_status():
    if not table_exists( 'thread_status', db=db ):
        sql = '''
            CREATE TABLE thread_status (
                id SERIAL PRIMARY KEY,
                thread_status_name CHARACTER VARYING(512) NOT NULL,
                meta_name CHARACTER VARYING(512),
                is_closed boolean DEFAULT false NOT NULL,
                preferred_order INTEGER DEFAULT 0 NOT NULL
            )
        '''
        db.executesql( sql )


def init_thread_type():
    if not table_exists( 'thread_type', db=db ):
        sql = '''
            CREATE TABLE thread_type (
                id SERIAL PRIMARY KEY,
                thread_type_name CHARACTER VARYING(512) NOT NULL,
                meta_name CHARACTER VARYING(512),
                preferred_order INTEGER DEFAULT 0 NOT NULL
            )
        '''
        db.executesql( sql )


def init_mime_type():
    if not table_exists( 'mime_type', db=db ):
        sql = '''
            CREATE TABLE mime_type (
                id SERIAL PRIMARY KEY,
                mt_name CHARACTER VARYING(512) NOT NULL,
                description CHARACTER VARYING(512),
                edit_command CHARACTER VARYING(512),
                view_command CHARACTER VARYING(512),
                preferred_order INTEGER DEFAULT 0 NOT NULL
            )
        '''
        db.executesql( sql )


def init_attach_type():
    if not table_exists( 'attach_type', db=db ):
        sql = '''
            CREATE TABLE attach_type (
                id SERIAL PRIMARY KEY,
                name CHARACTER VARYING(128) NOT NULL,
                meta_name CHARACTER VARYING(80)
            )
        '''
        db.executesql( sql )



def init_mime_type_ext():
    if not table_exists( 'c', db=db ):
        sql = '''
            CREATE TABLE mime_type_ext (
                id SERIAL PRIMARY KEY,
                mime_type_id INTEGER NOT NULL,
                extension CHARACTER VARYING(512) NOT NULL
            )
        '''
        db.executesql( sql )
    if not constraint_exists( 'mime_type_ext_2_mime_type', db=db ):
        sql = '''
            ALTER TABLE mime_type_ext
                ADD CONSTRAINT mime_type_ext_2_mime_type 
                FOREIGN KEY (mime_type_id) 
                REFERENCES mime_type( id )
        '''
        db.executesql( sql )


def init_app_config():
    if not table_exists( 'app_config', db=db ):
        sql = '''
            CREATE TABLE app_config (
                id SERIAL PRIMARY KEY,
                qt_decimals INTEGER NOT NULL,
                currency_decimals INTEGER NOT NULL,
                default_country_id integer,
                server_timezone CHARACTER VARYING(128) DEFAULT 'UTC'::CHARACTER VARYING NOT NULL,
                client_timezone CHARACTER VARYING(128) DEFAULT 'UTC'::CHARACTER VARYING NOT NULL,
                app_theme_id INTEGER DEFAULT 1 NOT NULL,
                flash_msg_delay INTEGER default 3000 not null,
                max_img_page_width INTEGER,
                max_img_block_width INTEGER,
                max_img_thumb_width INTEGER
            )
        '''
        db.executesql( sql )
    if not constraint_exists( 'app_config_2_app_theme', db=db ):
        sql = '''
            ALTER TABLE app_config
                ADD CONSTRAINT app_config_2_app_theme 
                FOREIGN KEY (app_theme_id) 
                REFERENCES app_theme(id)
        '''
        db.executesql( sql )


def init_attach():
    if not table_exists( 'attach', db=db ):
        sql = '''
            CREATE TABLE attach (
                id SERIAL PRIMARY KEY,
                attach_type_id INTEGER NOT NULL,
                attached CHARACTER VARYING(512),
                created_on timestamp without time zone DEFAULT now() NOT NULL,
                created_by INTEGER,
                path CHARACTER VARYING(512),
                filename CHARACTER VARYING(512),
                short_description CHARACTER VARYING(512),
                long_description CHARACTER VARYING,
                unit_type_id INTEGER,
                mime_type_id INTEGER,
                is_site_image boolean DEFAULT false NOT NULL,
                img_width INTEGER,
                img_height INTEGER,
                attached_file bytea,
                org_attach_id INTEGER
            )
        '''
        db.executesql( sql )
    if not constraint_exists( 'attach_2_attach_type', db=db ):
        sql = '''
            ALTER TABLE attach
                ADD CONSTRAINT attach_2_attach_type 
                FOREIGN KEY (attach_type_id) 
                REFERENCES attach_type(id)
        '''
        db.executesql( sql )
    if not constraint_exists( 'attach_2_unit_type', db=db ):
        sql = '''
            ALTER TABLE attach
                ADD CONSTRAINT attach_2_unit_type 
                FOREIGN KEY (unit_type_id) 
                REFERENCES unit_type(id)
        '''
        db.executesql( sql )
    if not constraint_exists( 'attach_2_mime_type', db=db ):
        sql = '''
            ALTER TABLE attach
                ADD CONSTRAINT attach_2_mime_type 
                FOREIGN KEY (mime_type_id) 
                REFERENCES mime_type(id)
        '''
        db.executesql( sql )


def init_auth():
    # auth_cas
    if not table_exists( 'auth_cas' ):
        sql = '''
            CREATE TABLE auth_cas (
                id SERIAL PRIMARY KEY,
                user_id INTEGER,
                created_on timestamp without time zone,
                service CHARACTER VARYING(512),
                ticket CHARACTER VARYING(512),
                renew character(1)
            )
        '''
        db.executesql( sql )

    # auth_event
    if not table_exists( 'auth_event' ):
        sql = '''
            CREATE TABLE auth_event (
                id SERIAL PRIMARY KEY,
                time_stamp timestamp without time zone,
                client_ip CHARACTER VARYING(512),
                user_id INTEGER,
                origin CHARACTER VARYING(512),
                description CHARACTER VARYING
            )
        '''
        db.executesql( sql )

    # auth_group
    if not table_exists( 'auth_group' ):
        sql = '''
            CREATE TABLE auth_group (
                id SERIAL PRIMARY KEY,
                role CHARACTER VARYING(512) NOT NULL,
                description CHARACTER VARYING
            )
        '''
        db.executesql( sql )
    if not index_exists( 'auth_group', 'auth_group_role_ukey' ):
        sql = '''
            create unique index auth_group_role_ukey
                on auth_group ( role )
        '''
        db.executesql( sql )

    # auth_user
    if not table_exists( 'auth_user' ):
        sql = '''
            CREATE TABLE auth_user (
                id SERIAL PRIMARY KEY,
                first_name CHARACTER VARYING(128) NOT NULL,
                last_name CHARACTER VARYING(128) NOT NULL DEFAULT '',
                email CHARACTER VARYING(512) NOT NULL,
                password CHARACTER VARYING(512),
                registration_key CHARACTER VARYING(512),
                reset_password_key CHARACTER VARYING(512),
                registration_id CHARACTER VARYING(512),
                user_timezone CHARACTER VARYING(128),
                ctime timestamp with time zone
            );
        '''
        db.executesql( sql )
    if not index_exists( 'auth_user', 'auth_user_name_ukey' ):
        sql = '''
            create unique index auth_group_name_ukey
                on auth_user ( first_name, last_name )
        '''
        db.executesql( sql )
    if not index_exists( 'auth_user', 'auth_user_email_ukey' ):
        sql = '''
            create unique index auth_group_email_ukey
                on auth_user ( email )
        '''
        db.executesql( sql )

    # auth_membership
    if not table_exists( 'auth_membership' ):
        sql = '''
            CREATE TABLE auth_membership (
                id SERIAL PRIMARY KEY,
                user_id INTEGER,
                group_id INTEGER
            )
        '''
        db.executesql( sql )
    if not index_exists( 'auth_membership', 'auth_membership_user_group_ukey' ):
        sql = '''
            create unique index auth_membership_user_group_ukey
                on auth_membership ( user_id, group_id )
        '''
        db.executesql( sql )
    if not constraint_exists( 'auth_membership_2_auth_user', db=db ):
        sql = '''
            ALTER TABLE auth_membership
                ADD CONSTRAINT auth_membership_2_auth_user 
                FOREIGN KEY (user_id) 
                REFERENCES auth_user(id)
        '''
        db.executesql( sql )
    if not constraint_exists( 'auth_membership_2_auth_group', db=db ):
        sql = '''
            ALTER TABLE auth_membership
                ADD CONSTRAINT auth_membership_2_auth_group 
                FOREIGN KEY (group_id) 
                REFERENCES auth_group(id)
        '''
        db.executesql( sql )

    # auth_permission
    if not table_exists( 'auth_permission' ):
        sql = '''
            CREATE TABLE auth_permission (
                id SERIAL PRIMARY KEY,
                group_id INTEGER,
                name CHARACTER VARYING(512),
                table_name CHARACTER VARYING(512),
                record_id INTEGER
            )
        '''
        db.executesql( sql )
    if not constraint_exists( 'auth_permission_2_auth_group', db=db ):
        sql = '''
            ALTER TABLE auth_permission
                ADD CONSTRAINT auth_permission_2_auth_group 
                FOREIGN KEY (group_id) 
                REFERENCES auth_group(id)
        '''
        db.executesql( sql )


def init_page():
    if not table_exists( 'page', db=db ):
        sql = '''
            CREATE TABLE page (
                id SERIAL PRIMARY KEY,
                parent_page_id INTEGER,
                tagname CHARACTER VARYING(512),
                title CHARACTER VARYING(1024) NOT NULL,
                title_en CHARACTER VARYING(1024),
                aside_title CHARACTER VARYING(512),
                aside_title_en CHARACTER VARYING(512),
                aside_position character(1),
                url_c CHARACTER VARYING(512),
                url_f CHARACTER VARYING(512),
                url_args CHARACTER VARYING(1024),
                colspan INTEGER DEFAULT 1 NOT NULL,
                rowspan INTEGER DEFAULT 1 NOT NULL,
                menu_order INTEGER,
                last_modified_by INTEGER NOT NULL,
                is_news boolean DEFAULT false NOT NULL,
                page_timestamp timestamp without time zone,
                name CHARACTER VARYING(512) NOT NULL,
                main_panel_cols INTEGER,
                aside_panel_cols INTEGER,
                hide boolean DEFAULT false
            )
        '''
        db.executesql( sql )
    if not constraint_exists( 'page_2_parent_page', db=db ):
        sql = '''
            ALTER TABLE page
                ADD CONSTRAINT page_2_parent_page 
                FOREIGN KEY (parent_page_id) 
                REFERENCES page(id)
        '''
        db.executesql( sql )


def init_block():
    if not table_exists( 'block', db=db ):
        sql = '''
            CREATE TABLE block (
                id SERIAL PRIMARY KEY,
                name CHARACTER VARYING(512),
                description CHARACTER VARYING(1024),
                page_id INTEGER,
                container character(1) DEFAULT 'M'::bpchar,
                blk_order INTEGER DEFAULT 1,
                body CHARACTER VARYING NOT NULL,
                body_en CHARACTER VARYING,
                body_markup character(1) DEFAULT 'M'::bpchar NOT NULL,
                created_on timestamp without time zone DEFAULT now() NOT NULL,
                created_by INTEGER NOT NULL,
                last_modified_by INTEGER NOT NULL,
                last_modified_on timestamp with time zone DEFAULT now(),
                colspan INTEGER DEFAULT 1 NOT NULL,
                rowspan INTEGER DEFAULT 1 NOT NULL,
                css_class CHARACTER VARYING(512),
                css_style CHARACTER VARYING(512),
                html_element_id CHARACTER VARYING(512)
            )
        '''
        db.executesql( sql )
        db.executesql( "COMMENT ON COLUMN block.container IS 'M: main; A: aside';" )
    if not constraint_exists( 'block_2_page', db=db ):
        sql = '''
            ALTER TABLE block
                ADD CONSTRAINT block_2_page 
                FOREIGN KEY (page_id) 
                REFERENCES page(id)
        '''
        db.executesql( sql )


def init_block_attach():
    if not table_exists( 'block_attach', db=db ):
        sql = '''
            CREATE TABLE block_attach (
                id SERIAL PRIMARY KEY,
                block_id INTEGER,
                attach_id INTEGER
            )
        '''
        db.executesql( sql )
    if not constraint_exists( 'block_attach_2_attach', db=db ):
        sql = '''
            ALTER TABLE block_attach
                ADD CONSTRAINT block_attach_2_attach 
                FOREIGN KEY (attach_id) 
                REFERENCES attach(id)
        '''
        db.executesql( sql )
    if not constraint_exists( 'block_attach_2_block', db=db ):
        sql = '''
            ALTER TABLE block_attach
                ADD CONSTRAINT block_attach_2_block 
                FOREIGN KEY (block_id) 
                REFERENCES block(id)
        '''
        db.executesql( sql )


def init_mail_queue():
    if not table_exists( 'mail_queue', db=db ):
        sql = '''
            CREATE TABLE mail_queue (
                id SERIAL PRIMARY KEY,
                subject CHARACTER VARYING(512) NOT NULL,
                text_body CHARACTER VARYING,
                html_body CHARACTER VARYING,
                when_to_send timestamp without time zone DEFAULT now() NOT NULL,
                sent timestamp without time zone,
                status CHARACTER VARYING(4096) NOT NULL,
                mail_cc CHARACTER VARYING(512),
                mail_bcc CHARACTER VARYING(512),
                auth_user_id INTEGER NOT NULL,
                percent_done INTEGER DEFAULT 0 NOT NULL,
                progress_message CHARACTER VARYING(2048)
            )
        '''
        db.executesql( sql )
        db.executesql( "COMMENT ON COLUMN mail_queue.status IS 'error, pending, sent or empty (for queued)'")
    if not constraint_exists( 'mail_queue_2_auth_user', db=db ):
        sql = '''
            ALTER TABLE mail_queue
                ADD CONSTRAINT mail_queue_2_auth_user 
                FOREIGN KEY (auth_user_id) 
                REFERENCES auth_user(id)
        '''
        db.executesql( sql )


def init_mail_recipient():
    if not table_exists( 'mail_recipient', db=db ):
        sql = '''
            CREATE TABLE mail_recipient (
                id SERIAL PRIMARY KEY,
                mail_queue_id INTEGER NOT NULL,
                email CHARACTER VARYING(512) NOT NULL,
                sent timestamp without time zone,
                status CHARACTER VARYING(4096) DEFAULT 'pending'::CHARACTER VARYING NOT NULL,
                retries INTEGER DEFAULT 0 NOT NULL
            );
        '''
        db.executesql( sql )
    if not constraint_exists( 'mail_recipient_2_mail_queue', db=db ):
        sql = '''
            ALTER TABLE mail_recipient
                ADD CONSTRAINT mail_recipient_2_mail_queue 
                FOREIGN KEY (mail_queue_id) 
                REFERENCES mail_queue(id)
        '''
        db.executesql( sql )


def init_page_log():
    if not table_exists( 'page_log', db=db ):
        sql = '''
            CREATE TABLE page_log (
                id SERIAL PRIMARY KEY,
                path_info CHARACTER VARYING(512) NOT NULL,
                ts timestamp without time zone NOT NULL,
                client_ip CHARACTER VARYING(16),
                auth_user_id INTEGER,
                is_tablet boolean default false,
                is_mobile boolean default false,
                os_name character varying(64),
                browser_name character varying(64),
                browser_version character varying(64)      
            )
        '''
        db.executesql( sql )
    if not constraint_exists( 'page_log_2_auth_user', db=db ):
        sql = '''
            ALTER TABLE page_log
                ADD CONSTRAINT page_log_2_auth_user 
                FOREIGN KEY (auth_user_id) 
                REFERENCES auth_user(id)
        '''
        db.executesql( sql )


def init_shared_run():
    if not table_exists( 'shared_run', db=db ):
        sql = '''
            CREATE TABLE shared_run (
                id SERIAL PRIMARY KEY,
                long_task_id INTEGER NOT NULL,
                task_parameters CHARACTER VARYING(4096),
                progress_message CHARACTER VARYING(4096),
                requested_by INTEGER,
                requested_when timestamp with time zone DEFAULT now() NOT NULL,
                start_at timestamp with time zone DEFAULT now() NOT NULL,
                running_since timestamp with time zone,
                finished_when timestamp with time zone,
                finished_status CHARACTER VARYING(1024),
                percent_done INTEGER DEFAULT 0 NOT NULL,
                notify_user boolean DEFAULT true NOT NULL,
                user_notified_when timestamp with time zone,
                progress_msg_id INTEGER,
                priority INTEGER DEFAULT 100 NOT NULL
            )
        '''
        db.executesql( sql )
    if not constraint_exists( 'shared_run_2_long_task', db=db ):
        sql = '''
            ALTER TABLE shared_run
                ADD CONSTRAINT shared_run_2_long_task 
                FOREIGN KEY (long_task_id) 
                REFERENCES long_task(id)
        '''
        db.executesql( sql )
    if not constraint_exists( 'shared_run_2_auth_user', db=db ):
        sql = '''
            ALTER TABLE shared_run
                ADD CONSTRAINT shared_run_2_auth_user 
                FOREIGN KEY (requested_by) 
                REFERENCES auth_user(id)
        '''
        db.executesql( sql )


def init_thread():
    if not table_exists( 'thread', db=db ):
        sql = '''
            CREATE TABLE thread (
                id SERIAL PRIMARY KEY,
                created_on timestamp without time zone NOT NULL,
                created_by INTEGER NOT NULL,
                thread_title CHARACTER VARYING(512) NOT NULL,
                thread_msg CHARACTER VARYING(65535),
                thread_status_id INTEGER DEFAULT 1 NOT NULL,
                thread_type_id INTEGER DEFAULT 1 NOT NULL,
                closed_time timestamp without time zone,
                markup character(1) DEFAULT 'M'::bpchar
            );
        '''
        db.executesql( sql )
        db.executesql( "COMMENT ON COLUMN thread.markup IS 'M: MARKMIN; H: HTML'")
    if not constraint_exists( 'thread_2_auth_user', db=db ):
        sql = '''
            ALTER TABLE thread
                ADD CONSTRAINT thread_2_auth_user 
                FOREIGN KEY (created_by) 
                REFERENCES auth_user(id)
        '''
        db.executesql( sql )
    if not constraint_exists( 'thread_2_thread_status', db=db ):
        sql = '''
            ALTER TABLE thread
                ADD CONSTRAINT thread_2_thread_status 
                FOREIGN KEY (thread_status_id) 
                REFERENCES thread_status(id)
        '''
        db.executesql( sql )
    if not constraint_exists( 'thread_2_thread_type', db=db ):
        sql = '''
            ALTER TABLE thread
                ADD CONSTRAINT thread_2_thread_type 
                FOREIGN KEY (thread_type_id) 
                REFERENCES thread_type(id)
        '''
        db.executesql( sql )


def init_thread_attach():
    if not table_exists( 'thread_attach', db=db ):
        sql = '''
            CREATE TABLE thread_attach (
                id SERIAL PRIMARY KEY,
                attach_id INTEGER,
                thread_id INTEGER
            );
        '''
        db.executesql( sql )
    if not constraint_exists( 'thread_attach_2_attach', db=db ):
        sql = '''
            ALTER TABLE thread_attach
                ADD CONSTRAINT thread_attach_2_attach 
                FOREIGN KEY (attach_id) 
                REFERENCES attach(id)
        '''
        db.executesql( sql )
    if not constraint_exists( 'thread_attach_2_thread', db=db ):
        sql = '''
            ALTER TABLE thread_attach
                ADD CONSTRAINT thread_attach_2_thread 
                FOREIGN KEY (thread_id) 
                REFERENCES thread(id)
        '''
        db.executesql( sql )


def init_thread_msg():
    if not table_exists( 'thread_msg', db=db ):
        sql = '''
            CREATE TABLE thread_msg (
                id SERIAL PRIMARY KEY,
                thread_id INTEGER NOT NULL,
                parent_thread_msg_id INTEGER,
                auth_user_id INTEGER NOT NULL,
                msg_text CHARACTER VARYING NOT NULL,
                msg_ts timestamp without time zone NOT NULL
            );
        '''
        db.executesql( sql )
    if not constraint_exists( 'thread_msg_2_thread', db=db ):
        sql = '''
            ALTER TABLE thread_msg
                ADD CONSTRAINT thread_msg_2_thread 
                FOREIGN KEY (thread_id) 
                REFERENCES thread(id)
        '''
        db.executesql( sql )
    if not constraint_exists( 'thread_msg_2_auth_user', db=db ):
        sql = '''
            ALTER TABLE thread_msg
                ADD CONSTRAINT thread_msg_2_auth_user 
                FOREIGN KEY (auth_user_id) 
                REFERENCES auth_user(id)
        '''
        db.executesql( sql )


def init_thread_msg_attach():
    if not table_exists( 'thread_msg_attach', db=db ):
        sql = '''
            CREATE TABLE thread_msg_attach (
                id SERIAL PRIMARY KEY,
                attach_id INTEGER,
                thread_msg_id INTEGER
            );
        '''
        db.executesql( sql )
    if not constraint_exists( 'thread_msg_attach_2_attach', db=db ):
        sql = '''
            ALTER TABLE thread_msg_attach
                ADD CONSTRAINT thread_msg_attach_2_attach 
                FOREIGN KEY (attach_id) 
                REFERENCES attach(id)
        '''
        db.executesql( sql )
    if not constraint_exists( 'thread_msg_attach_2_thread_msg', db=db ):
        sql = '''
            ALTER TABLE thread_msg_attach
                ADD CONSTRAINT thread_attach_msg_2_thread_msg 
                FOREIGN KEY (thread_msg_id) 
                REFERENCES thread_msg(id)
        '''
        db.executesql( sql )


def init_thread_subscriber():
    if not table_exists( 'thread_subscriber', db=db ):
        sql = '''
            CREATE TABLE thread_subscriber (
                id SERIAL PRIMARY KEY,
                thread_id INTEGER NOT NULL,
                auth_user_id INTEGER NOT NULL,
                unsubscribed timestamp without time zone
            );
        '''
        db.executesql( sql )
    if not constraint_exists( 'thread_subscriber_2_auth_user', db=db ):
        sql = '''
            ALTER TABLE thread_subscriber
                ADD CONSTRAINT thread_subscriber_2_auth_user 
                FOREIGN KEY (auth_user_id) 
                REFERENCES auth_user(id)
        '''
        db.executesql( sql )
    if not constraint_exists( 'thread_subscriber_2_thread', db=db ):
        sql = '''
            ALTER TABLE thread_subscriber
                ADD CONSTRAINT thread_subscriber_2_thread 
                FOREIGN KEY (thread_id) 
                REFERENCES thread(id)
        '''
        db.executesql( sql )


def init_thread_vote():
    if not table_exists( 'thread_vote', db=db ):
        sql = '''
            CREATE TABLE thread_vote (
                id SERIAL PRIMARY KEY,
                thread_id INTEGER NOT NULL,
                thread_msg_id INTEGER,
                auth_user_id INTEGER NOT NULL,
                vote_ts timestamp without time zone NOT NULL,
                vote INTEGER NOT NULL,
                CONSTRAINT thread_vote_vote_check CHECK (((vote = 1) OR (vote = '-1'::INTEGER)))
            )
        '''
        db.executesql( sql )
    if not constraint_exists( 'thread_vote_2_auth_user', db=db ):
        sql = '''
            ALTER TABLE thread_vote
                ADD CONSTRAINT thread_vote_2_auth_user 
                FOREIGN KEY (auth_user_id) 
                REFERENCES auth_user(id)
        '''
        db.executesql( sql )
    if not constraint_exists( 'thread_vote_2_thread', db=db ):
        sql = '''
            ALTER TABLE thread_vote
                ADD CONSTRAINT thread_vote_2_thread 
                FOREIGN KEY (thread_id) 
                REFERENCES thread(id)
        '''
        db.executesql( sql )
    if not constraint_exists( 'thread_vote_2_thread_msg', db=db ):
        sql = '''
            ALTER TABLE thread_vote
                ADD CONSTRAINT thread_vote_2_thread_msg
                FOREIGN KEY (thread_msg_id) 
                REFERENCES thread_msg(id)
        '''
        db.executesql( sql )


def init_user_message():
    if not table_exists( 'user_message', db=db ):
        sql = '''
            CREATE TABLE user_message (
                id SERIAL PRIMARY KEY,
                notify_user_id INTEGER NOT NULL,
                msg_org INTEGER,
                msg_title CHARACTER VARYING(512) NOT NULL,
                msg_text CHARACTER VARYING(4096) NOT NULL,
                times_viewed INTEGER NOT NULL,
                period_start timestamp with time zone DEFAULT now() NOT NULL,
                period_stop timestamp with time zone,
                ack_when timestamp without time zone,
                answer CHARACTER VARYING(4096),
                delete_if_past boolean DEFAULT false NOT NULL,
                msg_type CHARACTER VARYING(16)
            )
        '''
        db.executesql( sql )
    if not constraint_exists( 'user_message_2_auth_user', db=db ):
        sql = '''
            ALTER TABLE user_message
                ADD CONSTRAINT user_message_2_auth_user 
                FOREIGN KEY (notify_user_id) 
                REFERENCES auth_user(id)
        '''
        db.executesql( sql )


def init_country():
    if not table_exists( 'country', db=db ):
        sql = '''
            CREATE TABLE country (
                id SERIAL PRIMARY KEY,
                iso3166_1_alpha_2 CHAR(2) NOT NULL,
                name CHARACTER VARYING(256) NOT NULL,
                preferred_order INTEGER DEFAULT 0 NOT NULL
            )
        '''
        db.executesql( sql )
    if not index_exists( 'country', 'country_name_ukey' ):
        sql = '''
            create unique index country_name_ukey
                on country ( name )
        '''
        db.executesql( sql )
    if not index_exists( 'country', 'country_iso3166_ukey' ):
        sql = '''
            create unique index country_iso3166_ukey
                on country ( iso3166_1_alpha_2 )
        '''
        db.executesql( sql )


def init_country_region():
    if not table_exists( 'country_region', db=db ):
        sql = '''
            CREATE TABLE country_region (
                id SERIAL PRIMARY KEY,
                country_id INTEGER NOT NULL,
                name CHARACTER VARYING(128) NOT NULL,
                nuts_code CHARACTER VARYING(32) NOT NULL,
                preferred_order INTEGER DEFAULT 0 NOT NULL
            )
        '''
        db.executesql( sql )
    if not index_exists( 'country_region', 'country_region_country_nuts_ukey' ):
        sql = '''
            create unique index country_region_country_nuts_ukey
                on country_region ( country_id, nuts_code )
        '''
        db.executesql( sql )
    if not constraint_exists( 'country_region_2_country', db=db ):
        sql = '''
            ALTER TABLE country_region
                ADD CONSTRAINT country_region_2_country 
                FOREIGN KEY (country_id) 
                REFERENCES country(id)
        '''
        db.executesql( sql )


def init_district():
    if not table_exists( 'district', db=db ):
        sql = '''
            CREATE TABLE district (
                id SERIAL PRIMARY KEY,
                country_id INTEGER NOT NULL,
                country_region_id INTEGER NOT NULL,
                name CHARACTER VARYING(128) NOT NULL
            )
        '''
        db.executesql( sql )
    if not constraint_exists( 'district_2_country_2', db=db ):
        sql = '''
            ALTER TABLE district
                ADD CONSTRAINT district_2_country_2 
                FOREIGN KEY (country_id) 
                REFERENCES country(id)
        '''
        db.executesql( sql )
    if not constraint_exists( 'district_2_country_region_2', db=db ):
        sql = '''
            ALTER TABLE district
                ADD CONSTRAINT district_2_country_region_2 
                FOREIGN KEY (country_region_id) 
                REFERENCES country_region(id)
        '''
        db.executesql( sql )


from m16e import kommon, user_factory, term


def populate_users():
    T = current.T
    # admin user
    print( '''
        Please fill the main user (administrator) data below.
    ''')
    request = current.request
    cfg_file = request.env.web2py_path + '/applications/%(app)s/resources/config/init/cfg_%(app)s.py' % dict( app=current.app_name )
    term.printDebug( 'cfg_file: ' + cfg_file )
    from m16e.files import fileutils
    if fileutils.file_exists( cfg_file ):
        data = fileutils.read_data_file( cfg_file )
        first_name = data[ 'full_name']
        email = data[ 'email']
        password = data[ 'password']
    else:
        first_name = raw_input( T( 'Full name' ) + ': ' )
        email = raw_input( T( 'E-mail' ) + ': ' )
        password = getpass( T( 'Password' ) + ': ' )
    user_id = db.auth_user.insert( first_name=first_name,
                                   last_name='',
                                   email=email,
                                   password=db.auth_user.password.requires( password )[0] )
    for g in (user_factory._group_hierarchy_list ):
        g_id = db.auth_group.insert( role=g )
        db.auth_membership.insert( user_id=user_id, group_id=g_id )
    # dummy user (robot)
    db.auth_user.insert( first_name='(dummy)',
                         email=user_factory.DUMMY_USER,
                         registration_key='dummy' ) # prevent login


def populate_types():
    T = current.T
    from m16e.db import db_tables
    # attach_type
    at_model = db_tables.get_table_model( 'attach_type' )
    values = [ dict( name='Logo', meta_name='company-logo' ),
               dict( name='Fotos', meta_name='images' ),
               dict( name='Webshop', meta_name='webshop' ) ]
    for v in values:
        at_model.insert( v )
    # long_task
    lt_model = db_tables.get_table_model( 'long_task' )
    values = [ dict( task_name='send_mails', force_single_instance=True ) ]
    for v in values:
        lt_model.insert( v )
    # thread_type
    tt_model = db_tables.get_table_model( 'thread_type' )
    values = [ dict( thread_type_name=T( 'Open discussion' ), meta_name='open-discussion', preferred_order=1 ),
               dict( thread_type_name=T( 'Private discussion' ), meta_name='restricted', preferred_order=10 ),]
    for v in values:
        tt_model.insert( v )
    # app_theme
    appt_model = db_tables.get_table_model( 'app_theme' )
    values = [ dict( name='Chirico',
                     title='Chirico CMS',
                     subtitle='A free content management system',
                     logo_header='logo-64x64.png',
                     login_button_position='menu',
                     meta_name='chirico',
                     stylesheet='chirico' )
               ]
    for v in values:
        at_id = appt_model.insert( v )
    # app_config
    ac_model = db_tables.get_table_model( 'app_config' )
    values = [ dict( qt_decimals=0,
                     currency_decimals=0,
                     server_timezone='UTC',
                     client_timezone='UTC',
                     app_theme_id=at_id,
                     max_img_page_width=2048,
                     max_img_block_width=800,
                     max_img_thumb_width=160 )
               ]
    for v in values:
        ac_model.insert( v )


def populate_mime_types():
    from m16e.db import db_tables
    mt_model = db_tables.get_table_model( 'mime_type' )
    values = [ dict( mt_name='application/msword', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/octet-stream', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/ogg', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/pdf', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/pgp-keys', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/pgp-signature', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/postscript', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/rar', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/rdf+xml', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/rss+xml', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.ms-excel', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.ms-powerpoint', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.oasis.opendocument.chart', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.oasis.opendocument.database', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.oasis.opendocument.formula', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.oasis.opendocument.graphics', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.oasis.opendocument.graphics-template', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.oasis.opendocument.image', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.oasis.opendocument.presentation', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.oasis.opendocument.presentation-template', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.oasis.opendocument.spreadsheet', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.oasis.opendocument.spreadsheet-template', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.oasis.opendocument.text', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.oasis.opendocument.text-master', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.oasis.opendocument.text-template', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.oasis.opendocument.text-web', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.stardivision.calc', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.stardivision.draw', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.stardivision.impress', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.stardivision.math', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.stardivision.writer', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.stardivision.writer-global', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.sun.xml.calc', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.sun.xml.calc.template', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.sun.xml.draw', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.sun.xml.draw.template', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.sun.xml.impress', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.sun.xml.impress.template', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.sun.xml.math', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.sun.xml.writer', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.sun.xml.writer.global', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/vnd.sun.xml.writer.template', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/x-dvi', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/x-flac', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/x-font', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/x-freemind', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/x-gnumeric', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/x-gtar', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/x-java-jnlp-file', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/x-kpresenter', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/x-kspread', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/x-kword', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/xml', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/x-shockwave-flash', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/x-tar', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='application/zip', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='audio/basic', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='audio/midi', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='audio/mpeg', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='audio/mpegurl', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='audio/x-aiff', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='audio/x-mpegurl', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='audio/x-ms-wma', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='audio/x-pn-realaudio', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='audio/x-realaudio', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='audio/x-wav', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='(desconhecido)', description='(tipo deconhecido)', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='image/gif', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='image/jpeg', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='image/png', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='image/svg+xml', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='image/tiff', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='image/vnd.djvu', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='image/x-coreldraw', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='image/x-coreldrawpattern', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='image/x-coreldrawtemplate', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='image/x-corelphotopaint', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='image/x-icon', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='image/x-ms-bmp', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='image/x-photoshop', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='image/x-portable-anymap', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='image/x-portable-bitmap', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='image/x-portable-graymap', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='image/x-portable-pixmap', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='image/x-rgb', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='image/x-xbitmap', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='image/x-xpixmap', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='image/x-xwindowdump', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='text/html', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='text/plain', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='text/richtext', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='text/rtf', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='video/mp4', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='video/mpeg', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='video/quicktime', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='video/x-ms-wmv', description='', edit_command='', view_command='', preferred_order=1 ),
               dict( mt_name='video/x-sgi-movie', description='', edit_command='', view_command='', preferred_order=1 ),
    ]
    for v in values:
        mt_model.insert( v )

    mte_model = db_tables.get_table_model( 'mime_type_ext' )
    # mime_type_ext
    values = [ dict( mime_type_name='application/postscript', extension='ai' ),
               dict( mime_type_name='audio/x-aiff', extension='aif' ),
               dict( mime_type_name='audio/x-aiff', extension='aifc' ),
               dict( mime_type_name='audio/x-aiff', extension='aiff' ),
               dict( mime_type_name='text/plain', extension='asc' ),
               dict( mime_type_name='audio/basic', extension='au' ),
               dict( mime_type_name='application/octet-stream', extension='bin' ),
               dict( mime_type_name='image/x-ms-bmp', extension='bmp' ),
               dict( mime_type_name='image/x-coreldraw', extension='cdr' ),
               dict( mime_type_name='image/x-coreldrawtemplate', extension='cdt' ),
               dict( mime_type_name='image/x-corelphotopaint', extension='cpt' ),
               dict( mime_type_name='text/plain', extension='csv' ),
               dict( mime_type_name='text/plain', extension='diff' ),
               dict( mime_type_name='image/vnd.djvu', extension='djv' ),
               dict( mime_type_name='image/vnd.djvu', extension='djvu' ),
               dict( mime_type_name='application/msword', extension='doc' ),
               dict( mime_type_name='application/msword', extension='docx' ),
               dict( mime_type_name='application/msword', extension='dot' ),
               dict( mime_type_name='application/x-dvi', extension='dvi' ),
               dict( mime_type_name='application/postscript', extension='eps' ),
               dict( mime_type_name='application/x-flac', extension='flac' ),
               dict( mime_type_name='image/gif', extension='gif' ),
               dict( mime_type_name='application/x-gnumeric', extension='gnumeric' ),
               dict( mime_type_name='application/x-font', extension='gsf' ),
               dict( mime_type_name='application/x-gtar', extension='gtar' ),
               dict( mime_type_name='text/html', extension='htm' ),
               dict( mime_type_name='text/html', extension='html' ),
               dict( mime_type_name='image/x-icon', extension='ico' ),
               dict( mime_type_name='application/x-java-jnlp-file', extension='jnlp' ),
               dict( mime_type_name='image/jpeg', extension='jpe' ),
               dict( mime_type_name='image/jpeg', extension='jpeg' ),
               dict( mime_type_name='image/jpeg', extension='jpg' ),
               dict( mime_type_name='audio/midi', extension='kar' ),
               dict( mime_type_name='application/pgp-keys', extension='key' ),
               dict( mime_type_name='application/x-kpresenter', extension='kpr' ),
               dict( mime_type_name='application/x-kpresenter', extension='kpt' ),
               dict( mime_type_name='application/x-kspread', extension='ksp' ),
               dict( mime_type_name='application/x-kword', extension='kwd' ),
               dict( mime_type_name='application/x-kword', extension='kwt' ),
               dict( mime_type_name='audio/x-mpegurl', extension='m3u' ),
               dict( mime_type_name='audio/mpeg', extension='m4a' ),
               dict( mime_type_name='audio/midi', extension='mid' ),
               dict( mime_type_name='audio/midi', extension='midi' ),
               dict( mime_type_name='application/x-freemind', extension='mm' ),
               dict( mime_type_name='video/quicktime', extension='mov' ),
               dict( mime_type_name='video/x-sgi-movie', extension='movie' ),
               dict( mime_type_name='audio/mpeg', extension='mp2' ),
               dict( mime_type_name='audio/mpeg', extension='mp3' ),
               dict( mime_type_name='video/mp4', extension='mp4' ),
               dict( mime_type_name='video/mpeg', extension='mpe' ),
               dict( mime_type_name='video/mpeg', extension='mpeg' ),
               dict( mime_type_name='audio/mpeg', extension='mpega' ),
               dict( mime_type_name='video/mpeg', extension='mpg' ),
               dict( mime_type_name='audio/mpeg', extension='mpga' ),
               dict( mime_type_name='application/vnd.oasis.opendocument.database', extension='odb' ),
               dict( mime_type_name='application/vnd.oasis.opendocument.chart', extension='odc' ),
               dict( mime_type_name='application/vnd.oasis.opendocument.formula', extension='odf' ),
               dict( mime_type_name='application/vnd.oasis.opendocument.graphics', extension='odg' ),
               dict( mime_type_name='application/vnd.oasis.opendocument.image', extension='odi' ),
               dict( mime_type_name='application/vnd.oasis.opendocument.text-master', extension='odm' ),
               dict( mime_type_name='application/vnd.oasis.opendocument.presentation', extension='odp' ),
               dict( mime_type_name='application/vnd.oasis.opendocument.spreadsheet', extension='ods' ),
               dict( mime_type_name='application/vnd.oasis.opendocument.text', extension='odt' ),
               dict( mime_type_name='application/ogg', extension='ogg' ),
               dict( mime_type_name='application/vnd.oasis.opendocument.graphics-template', extension='otg' ),
               dict( mime_type_name='application/vnd.oasis.opendocument.text-web', extension='oth' ),
               dict( mime_type_name='application/vnd.oasis.opendocument.presentation-template', extension='otp' ),
               dict( mime_type_name='application/vnd.oasis.opendocument.spreadsheet-template', extension='ots' ),
               dict( mime_type_name='application/vnd.oasis.opendocument.text-template', extension='ott' ),
               dict( mime_type_name='image/x-coreldrawpattern', extension='pat' ),
               dict( mime_type_name='image/x-portable-bitmap', extension='pbm' ),
               dict( mime_type_name='application/x-font', extension='pcf' ),
               dict( mime_type_name='application/x-font', extension='pcf.Z' ),
               dict( mime_type_name='application/pdf', extension='pdf' ),
               dict( mime_type_name='application/x-font', extension='pfa' ),
               dict( mime_type_name='application/x-font', extension='pfb' ),
               dict( mime_type_name='image/x-portable-graymap', extension='pgm' ),
               dict( mime_type_name='application/pgp-signature', extension='pgp' ),
               dict( mime_type_name='image/png', extension='png' ),
               dict( mime_type_name='image/x-portable-anymap', extension='pnm' ),
               dict( mime_type_name='text/plain', extension='pot' ),
               dict( mime_type_name='image/x-portable-pixmap', extension='ppm' ),
               dict( mime_type_name='application/vnd.ms-powerpoint', extension='pps' ),
               dict( mime_type_name='application/vnd.ms-powerpoint', extension='ppt' ),
               dict( mime_type_name='application/postscript', extension='ps' ),
               dict( mime_type_name='image/x-photoshop', extension='psd' ),
               dict( mime_type_name='video/quicktime', extension='qt' ),
               dict( mime_type_name='audio/x-pn-realaudio', extension='ra' ),
               dict( mime_type_name='audio/x-pn-realaudio', extension='ram' ),
               dict( mime_type_name='application/rar', extension='rar' ),
               dict( mime_type_name='application/rdf+xml', extension='rdf' ),
               dict( mime_type_name='image/x-rgb', extension='rgb' ),
               dict( mime_type_name='audio/x-pn-realaudio', extension='rm' ),
               dict( mime_type_name='application/rss+xml', extension='rss' ),
               dict( mime_type_name='text/rtf', extension='rtf' ),
               dict( mime_type_name='text/richtext', extension='rtx' ),
               dict( mime_type_name='application/vnd.stardivision.draw', extension='sda' ),
               dict( mime_type_name='application/vnd.stardivision.calc', extension='sdc' ),
               dict( mime_type_name='application/vnd.stardivision.impress', extension='sdd' ),
               dict( mime_type_name='application/vnd.stardivision.impress', extension='sdp' ),
               dict( mime_type_name='application/vnd.stardivision.writer', extension='sdw' ),
               dict( mime_type_name='application/vnd.stardivision.writer-global', extension='sgl' ),
               dict( mime_type_name='text/html', extension='shtml' ),
               dict( mime_type_name='application/vnd.stardivision.math', extension='smf' ),
               dict( mime_type_name='audio/basic', extension='snd' ),
               dict( mime_type_name='application/vnd.sun.xml.calc.template', extension='stc' ),
               dict( mime_type_name='application/vnd.sun.xml.draw.template', extension='std' ),
               dict( mime_type_name='application/vnd.sun.xml.impress.template', extension='sti' ),
               dict( mime_type_name='application/vnd.sun.xml.writer.template', extension='stw' ),
               dict( mime_type_name='image/svg+xml', extension='svg' ),
               dict( mime_type_name='image/svg+xml', extension='svgz' ),
               dict( mime_type_name='application/x-shockwave-flash', extension='swf' ),
               dict( mime_type_name='application/x-shockwave-flash', extension='swfl' ),
               dict( mime_type_name='application/vnd.sun.xml.calc', extension='sxc' ),
               dict( mime_type_name='application/vnd.sun.xml.draw', extension='sxd' ),
               dict( mime_type_name='application/vnd.sun.xml.writer.global', extension='sxg' ),
               dict( mime_type_name='application/vnd.sun.xml.impress', extension='sxi' ),
               dict( mime_type_name='application/vnd.sun.xml.math', extension='sxm' ),
               dict( mime_type_name='application/vnd.sun.xml.writer', extension='sxw' ),
               dict( mime_type_name='application/x-tar', extension='tar' ),
               dict( mime_type_name='application/x-gtar', extension='taz' ),
               dict( mime_type_name='text/plain', extension='text' ),
               dict( mime_type_name='application/x-gtar', extension='tgz' ),
               dict( mime_type_name='image/tiff', extension='tif' ),
               dict( mime_type_name='image/tiff', extension='tiff' ),
               dict( mime_type_name='text/plain', extension='txt' ),
               dict( mime_type_name='application/vnd.stardivision.writer', extension='vor' ),
               dict( mime_type_name='audio/x-wav', extension='wav' ),
               dict( mime_type_name='audio/x-ms-wma', extension='wma' ),
               dict( mime_type_name='video/x-ms-wmv', extension='wmv' ),
               dict( mime_type_name='image/x-xbitmap', extension='xbm' ),
               dict( mime_type_name='application/vnd.ms-excel', extension='xlb' ),
               dict( mime_type_name='application/vnd.ms-excel', extension='xls' ),
               dict( mime_type_name='application/vnd.ms-excel', extension='xlsx' ),
               dict( mime_type_name='application/vnd.ms-excel', extension='xlt' ),
               dict( mime_type_name='application/xml', extension='xml' ),
               dict( mime_type_name='image/x-xpixmap', extension='xpm' ),
               dict( mime_type_name='application/xml', extension='xsl' ),
               dict( mime_type_name='image/x-xwindowdump', extension='xwd' ),
               dict( mime_type_name='application/zip', extension='zip' ),
    ]
    for v in values:
        q_sql = (db.mime_type.mt_name == v[ 'mime_type_name' ])
        mt = mt_model.select( q_sql ).first()
        mte_model.insert( dict( mime_type_id=mt.id, extension=v[ 'extension' ] ) )


def populate_countries():
    from m16e.db import db_tables
    # country
    c_model = db_tables.get_table_model( 'country' )
    values = [ dict( iso3166_1_alpha_2='PT', name='Portugal', preferred_order=0 ),
               dict( iso3166_1_alpha_2='AF', name='Afeganistão', preferred_order=1 ),
               dict( iso3166_1_alpha_2='ZA', name='África do Sul', preferred_order=2 ),
               dict( iso3166_1_alpha_2='AX', name='Åland, Ilhas', preferred_order=3 ),
               dict( iso3166_1_alpha_2='AL', name='Albânia', preferred_order=4 ),
               dict( iso3166_1_alpha_2='DE', name='Alemanha', preferred_order=5 ),
               dict( iso3166_1_alpha_2='AD', name='Andorra', preferred_order=6 ),
               dict( iso3166_1_alpha_2='AO', name='Angola', preferred_order=7 ),
               dict( iso3166_1_alpha_2='AI', name='Anguilla', preferred_order=8 ),
               dict( iso3166_1_alpha_2='AQ', name='Antárctida', preferred_order=9 ),
               dict( iso3166_1_alpha_2='AG', name='Antígua e Barbuda', preferred_order=10 ),
               dict( iso3166_1_alpha_2='AN', name='Antilhas Holandesas', preferred_order=11 ),
               dict( iso3166_1_alpha_2='SA', name='Arábia Saudita', preferred_order=12 ),
               dict( iso3166_1_alpha_2='DZ', name='Argélia', preferred_order=13 ),
               dict( iso3166_1_alpha_2='AR', name='Argentina', preferred_order=14 ),
               dict( iso3166_1_alpha_2='AM', name='Armênia', preferred_order=15 ),
               dict( iso3166_1_alpha_2='AW', name='Aruba', preferred_order=16 ),
               dict( iso3166_1_alpha_2='AU', name='Austrália', preferred_order=17 ),
               dict( iso3166_1_alpha_2='AT', name='Áustria', preferred_order=18 ),
               dict( iso3166_1_alpha_2='AZ', name='Azerbaijão', preferred_order=19 ),
               dict( iso3166_1_alpha_2='BS', name='Bahamas', preferred_order=20 ),
               dict( iso3166_1_alpha_2='BH', name='Bahrain', preferred_order=21 ),
               dict( iso3166_1_alpha_2='BD', name='Bangladesh', preferred_order=22 ),
               dict( iso3166_1_alpha_2='BB', name='Barbados', preferred_order=23 ),
               dict( iso3166_1_alpha_2='BE', name='Bélgica', preferred_order=24 ),
               dict( iso3166_1_alpha_2='BZ', name='Belize', preferred_order=25 ),
               dict( iso3166_1_alpha_2='BJ', name='Benim', preferred_order=26 ),
               dict( iso3166_1_alpha_2='BM', name='Bermudas', preferred_order=27 ),
               dict( iso3166_1_alpha_2='BY', name='Bielorrússia', preferred_order=28 ),
               dict( iso3166_1_alpha_2='BO', name='Bolívia', preferred_order=29 ),
               dict( iso3166_1_alpha_2='BA', name='Bósnia e Herzegovina', preferred_order=30 ),
               dict( iso3166_1_alpha_2='BW', name='Botswana', preferred_order=31 ),
               dict( iso3166_1_alpha_2='BV', name='Bouvet, Ilha', preferred_order=32 ),
               dict( iso3166_1_alpha_2='BR', name='Brasil', preferred_order=33 ),
               dict( iso3166_1_alpha_2='BN', name='Brunei', preferred_order=34 ),
               dict( iso3166_1_alpha_2='BG', name='Bulgária', preferred_order=35 ),
               dict( iso3166_1_alpha_2='BF', name='Burkina Faso', preferred_order=36 ),
               dict( iso3166_1_alpha_2='BI', name='Burundi', preferred_order=37 ),
               dict( iso3166_1_alpha_2='BT', name='Butão', preferred_order=38 ),
               dict( iso3166_1_alpha_2='CV', name='Cabo Verde', preferred_order=39 ),
               dict( iso3166_1_alpha_2='CM', name='Camarões', preferred_order=40 ),
               dict( iso3166_1_alpha_2='KH', name='Cambodja', preferred_order=41 ),
               dict( iso3166_1_alpha_2='CA', name='Canadá', preferred_order=42 ),
               dict( iso3166_1_alpha_2='KY', name='Cayman, Ilhas', preferred_order=43 ),
               dict( iso3166_1_alpha_2='KZ', name='Cazaquistão', preferred_order=44 ),
               dict( iso3166_1_alpha_2='CF', name='Centro-Africana, República', preferred_order=45 ),
               dict( iso3166_1_alpha_2='TD', name='Chade', preferred_order=46 ),
               dict( iso3166_1_alpha_2='CZ', name='Checa, República', preferred_order=47 ),
               dict( iso3166_1_alpha_2='CL', name='Chile', preferred_order=48 ),
               dict( iso3166_1_alpha_2='CN', name='China', preferred_order=49 ),
               dict( iso3166_1_alpha_2='CY', name='Chipre', preferred_order=50 ),
               dict( iso3166_1_alpha_2='CX', name='Christmas, Ilha', preferred_order=51 ),
               dict( iso3166_1_alpha_2='CC', name='Cocos, Ilhas', preferred_order=52 ),
               dict( iso3166_1_alpha_2='CO', name='Colômbia', preferred_order=53 ),
               dict( iso3166_1_alpha_2='KM', name='Comores', preferred_order=54 ),
               dict( iso3166_1_alpha_2='CD', name='Congo, República Democrática do (antigo Zaire)', preferred_order=55 ),
               dict( iso3166_1_alpha_2='CG', name='Congo, República do', preferred_order=56 ),
               dict( iso3166_1_alpha_2='CK', name='Cook, Ilhas', preferred_order=57 ),
               dict( iso3166_1_alpha_2='KR', name='Coréia do Sul', preferred_order=58 ),
               dict( iso3166_1_alpha_2='KP', name='Coreia, República Democrática da (Coreia do Norte)', preferred_order=59 ),
               dict( iso3166_1_alpha_2='CI', name='Costa do Marfim', preferred_order=60 ),
               dict( iso3166_1_alpha_2='CR', name='Costa Rica', preferred_order=61 ),
               dict( iso3166_1_alpha_2='HR', name='Croácia', preferred_order=62 ),
               dict( iso3166_1_alpha_2='CU', name='Cuba', preferred_order=63 ),
               dict( iso3166_1_alpha_2='DK', name='Dinamarca', preferred_order=64 ),
               dict( iso3166_1_alpha_2='DJ', name='Djibouti', preferred_order=65 ),
               dict( iso3166_1_alpha_2='DM', name='Dominica', preferred_order=66 ),
               dict( iso3166_1_alpha_2='DO', name='Dominicana, República', preferred_order=67 ),
               dict( iso3166_1_alpha_2='EG', name='Egito', preferred_order=68 ),
               dict( iso3166_1_alpha_2='SV', name='El Salvador', preferred_order=69 ),
               dict( iso3166_1_alpha_2='AE', name='Emirados Árabes Unidos', preferred_order=70 ),
               dict( iso3166_1_alpha_2='EC', name='Equador', preferred_order=71 ),
               dict( iso3166_1_alpha_2='ER', name='Eritreia', preferred_order=72 ),
               dict( iso3166_1_alpha_2='SK', name='Eslováquia', preferred_order=73 ),
               dict( iso3166_1_alpha_2='SI', name='Eslovênia', preferred_order=74 ),
               dict( iso3166_1_alpha_2='ES', name='Espanha', preferred_order=75 ),
               dict( iso3166_1_alpha_2='US', name='E.U.A.', preferred_order=76 ),
               dict( iso3166_1_alpha_2='EE', name='Estónia', preferred_order=77 ),
               dict( iso3166_1_alpha_2='ET', name='Etiópia', preferred_order=78 ),
               dict( iso3166_1_alpha_2='FO', name='Feroé, Ilhas', preferred_order=79 ),
               dict( iso3166_1_alpha_2='FJ', name='Fiji', preferred_order=80 ),
               dict( iso3166_1_alpha_2='PH', name='Filipinas', preferred_order=81 ),
               dict( iso3166_1_alpha_2='FI', name='Finlândia', preferred_order=82 ),
               dict( iso3166_1_alpha_2='FR', name='França', preferred_order=83 ),
               dict( iso3166_1_alpha_2='GA', name='Gabão', preferred_order=84 ),
               dict( iso3166_1_alpha_2='GM', name='Gâmbia', preferred_order=85 ),
               dict( iso3166_1_alpha_2='GH', name='Gana', preferred_order=86 ),
               dict( iso3166_1_alpha_2='GE', name='Geórgia', preferred_order=87 ),
               dict( iso3166_1_alpha_2='GS', name='Geórgia do Sul e Sandwich do Sul, Ilhas', preferred_order=88 ),
               dict( iso3166_1_alpha_2='GI', name='Gibraltar', preferred_order=89 ),
               dict( iso3166_1_alpha_2='GR', name='Grécia', preferred_order=90 ),
               dict( iso3166_1_alpha_2='GD', name='Grenada', preferred_order=91 ),
               dict( iso3166_1_alpha_2='GL', name='Groenlândia', preferred_order=92 ),
               dict( iso3166_1_alpha_2='GP', name='Guadalupe', preferred_order=93 ),
               dict( iso3166_1_alpha_2='GU', name='Guam', preferred_order=94 ),
               dict( iso3166_1_alpha_2='GT', name='Guatemala', preferred_order=95 ),
               dict( iso3166_1_alpha_2='GG', name='Guernsey', preferred_order=96 ),
               dict( iso3166_1_alpha_2='GY', name='Guiana', preferred_order=97 ),
               dict( iso3166_1_alpha_2='GF', name='Guiana Francesa', preferred_order=98 ),
               dict( iso3166_1_alpha_2='GW', name='Guiné-Bissau', preferred_order=99 ),
               dict( iso3166_1_alpha_2='GN', name='Guiné-Conacri', preferred_order=100 ),
               dict( iso3166_1_alpha_2='GQ', name='Guiné Equatorial', preferred_order=101 ),
               dict( iso3166_1_alpha_2='HT', name='Haiti', preferred_order=102 ),
               dict( iso3166_1_alpha_2='HM', name='Heard e Ilhas McDonald, Ilha', preferred_order=103 ),
               dict( iso3166_1_alpha_2='HN', name='Honduras', preferred_order=104 ),
               dict( iso3166_1_alpha_2='HK', name='Hong Kong', preferred_order=105 ),
               dict( iso3166_1_alpha_2='HU', name='Hungria', preferred_order=106 ),
               dict( iso3166_1_alpha_2='YE', name='Iémen', preferred_order=107 ),
               dict( iso3166_1_alpha_2='IN', name='Índia', preferred_order=108 ),
               dict( iso3166_1_alpha_2='ID', name='Indonésia', preferred_order=109 ),
               dict( iso3166_1_alpha_2='IR', name='Irã', preferred_order=110 ),
               dict( iso3166_1_alpha_2='IQ', name='Iraque', preferred_order=111 ),
               dict( iso3166_1_alpha_2='IE', name='Irlanda', preferred_order=112 ),
               dict( iso3166_1_alpha_2='IS', name='Islândia', preferred_order=113 ),
               dict( iso3166_1_alpha_2='IL', name='Israel', preferred_order=114 ),
               dict( iso3166_1_alpha_2='IT', name='Itália', preferred_order=115 ),
               dict( iso3166_1_alpha_2='JM', name='Jamaica', preferred_order=116 ),
               dict( iso3166_1_alpha_2='JP', name='Japão', preferred_order=117 ),
               dict( iso3166_1_alpha_2='JE', name='Jersey', preferred_order=118 ),
               dict( iso3166_1_alpha_2='JO', name='Jordânia', preferred_order=119 ),
               dict( iso3166_1_alpha_2='KI', name='Kiribati', preferred_order=120 ),
               dict( iso3166_1_alpha_2='KW', name='Kuwait', preferred_order=121 ),
               dict( iso3166_1_alpha_2='LA', name='Laos', preferred_order=122 ),
               dict( iso3166_1_alpha_2='LS', name='Lesoto', preferred_order=123 ),
               dict( iso3166_1_alpha_2='LV', name='Letônia', preferred_order=124 ),
               dict( iso3166_1_alpha_2='LB', name='Líbano', preferred_order=125 ),
               dict( iso3166_1_alpha_2='LR', name='Libéria', preferred_order=126 ),
               dict( iso3166_1_alpha_2='LY', name='Líbia', preferred_order=127 ),
               dict( iso3166_1_alpha_2='LI', name='Liechtenstein', preferred_order=128 ),
               dict( iso3166_1_alpha_2='LT', name='Lituânia', preferred_order=129 ),
               dict( iso3166_1_alpha_2='LU', name='Luxemburgo', preferred_order=130 ),
               dict( iso3166_1_alpha_2='MO', name='Macau', preferred_order=131 ),
               dict( iso3166_1_alpha_2='MK', name='Macedônia, República da', preferred_order=132 ),
               dict( iso3166_1_alpha_2='MG', name='Madagáscar', preferred_order=133 ),
               dict( iso3166_1_alpha_2='MY', name='Malásia', preferred_order=134 ),
               dict( iso3166_1_alpha_2='MW', name='Malawi', preferred_order=135 ),
               dict( iso3166_1_alpha_2='MV', name='Maldivas', preferred_order=136 ),
               dict( iso3166_1_alpha_2='ML', name='Mali', preferred_order=137 ),
               dict( iso3166_1_alpha_2='MT', name='Malta', preferred_order=138 ),
               dict( iso3166_1_alpha_2='FK', name='Malvinas, Ilhas (Falkland)', preferred_order=139 ),
               dict( iso3166_1_alpha_2='IM', name='Man, Ilha de', preferred_order=140 ),
               dict( iso3166_1_alpha_2='MP', name='Marianas Setentrionais', preferred_order=141 ),
               dict( iso3166_1_alpha_2='MA', name='Marrocos', preferred_order=142 ),
               dict( iso3166_1_alpha_2='MH', name='Marshall, Ilhas', preferred_order=143 ),
               dict( iso3166_1_alpha_2='MQ', name='Martinica', preferred_order=144 ),
               dict( iso3166_1_alpha_2='MU', name='Maurícia', preferred_order=145 ),
               dict( iso3166_1_alpha_2='MR', name='Mauritânia', preferred_order=146 ),
               dict( iso3166_1_alpha_2='YT', name='Mayotte', preferred_order=147 ),
               dict( iso3166_1_alpha_2='UM', name='Menores Distantes dos Estados Unidos, Ilhas', preferred_order=148 ),
               dict( iso3166_1_alpha_2='MX', name='México', preferred_order=149 ),
               dict( iso3166_1_alpha_2='FM', name='Micronésia, Estados Federados da', preferred_order=150 ),
               dict( iso3166_1_alpha_2='MZ', name='Moçambique', preferred_order=151 ),
               dict( iso3166_1_alpha_2='MD', name='Moldávia', preferred_order=152 ),
               dict( iso3166_1_alpha_2='MC', name='Mônaco', preferred_order=153 ),
               dict( iso3166_1_alpha_2='MN', name='Mongólia', preferred_order=154 ),
               dict( iso3166_1_alpha_2='ME', name='Montenegro', preferred_order=155 ),
               dict( iso3166_1_alpha_2='MS', name='Montserrat', preferred_order=156 ),
               dict( iso3166_1_alpha_2='MM', name='Myanmar (antiga Birmânia)', preferred_order=157 ),
               dict( iso3166_1_alpha_2='NA', name='Namíbia', preferred_order=158 ),
               dict( iso3166_1_alpha_2='NR', name='Nauru', preferred_order=159 ),
               dict( iso3166_1_alpha_2='NP', name='Nepal', preferred_order=160 ),
               dict( iso3166_1_alpha_2='NI', name='Nicarágua', preferred_order=161 ),
               dict( iso3166_1_alpha_2='NE', name='Níger', preferred_order=162 ),
               dict( iso3166_1_alpha_2='NG', name='Nigéria', preferred_order=163 ),
               dict( iso3166_1_alpha_2='NU', name='Niue', preferred_order=164 ),
               dict( iso3166_1_alpha_2='NF', name='Norfolk, Ilha', preferred_order=165 ),
               dict( iso3166_1_alpha_2='NO', name='Noruega', preferred_order=166 ),
               dict( iso3166_1_alpha_2='NC', name='Nova Caledônia', preferred_order=167 ),
               dict( iso3166_1_alpha_2='NZ', name='Nova Zelândia (Aotearoa)', preferred_order=168 ),
               dict( iso3166_1_alpha_2='OM', name='Oman', preferred_order=169 ),
               dict( iso3166_1_alpha_2='NL', name='Países Baixos (Holanda)', preferred_order=170 ),
               dict( iso3166_1_alpha_2='PW', name='Palau', preferred_order=171 ),
               dict( iso3166_1_alpha_2='PS', name='Palestina', preferred_order=172 ),
               dict( iso3166_1_alpha_2='PA', name='Panamá', preferred_order=173 ),
               dict( iso3166_1_alpha_2='PG', name='Papua-Nova Guiné', preferred_order=174 ),
               dict( iso3166_1_alpha_2='PK', name='Paquistão', preferred_order=175 ),
               dict( iso3166_1_alpha_2='PY', name='Paraguai', preferred_order=176 ),
               dict( iso3166_1_alpha_2='PE', name='Peru', preferred_order=177 ),
               dict( iso3166_1_alpha_2='PN', name='Pitcairn', preferred_order=178 ),
               dict( iso3166_1_alpha_2='PF', name='Polinésia Francesa', preferred_order=179 ),
               dict( iso3166_1_alpha_2='PL', name='Polônia', preferred_order=180 ),
               dict( iso3166_1_alpha_2='PR', name='Porto Rico', preferred_order=181 ),
               dict( iso3166_1_alpha_2='QA', name='Qatar', preferred_order=182 ),
               dict( iso3166_1_alpha_2='KE', name='Quênia', preferred_order=183 ),
               dict( iso3166_1_alpha_2='KG', name='Quirguistão', preferred_order=184 ),
               dict( iso3166_1_alpha_2='GB', name='Reino Unido da Grã-Bretanha e Irlanda do Norte', preferred_order=185 ),
               dict( iso3166_1_alpha_2='RE', name='Reunião', preferred_order=186 ),
               dict( iso3166_1_alpha_2='RO', name='Romênia', preferred_order=187 ),
               dict( iso3166_1_alpha_2='RW', name='Ruanda', preferred_order=188 ),
               dict( iso3166_1_alpha_2='RU', name='Rússia', preferred_order=189 ),
               dict( iso3166_1_alpha_2='EH', name='Saara Ocidental', preferred_order=190 ),
               dict( iso3166_1_alpha_2='PM', name='Saint Pierre et Miquelon', preferred_order=191 ),
               dict( iso3166_1_alpha_2='SB', name='Salomão, Ilhas', preferred_order=192 ),
               dict( iso3166_1_alpha_2='AS', name='Samoa Americana', preferred_order=193 ),
               dict( iso3166_1_alpha_2='WS', name='Samoa (Samoa Ocidental)', preferred_order=194 ),
               dict( iso3166_1_alpha_2='SM', name='San Marino', preferred_order=195 ),
               dict( iso3166_1_alpha_2='SH', name='Santa Helena', preferred_order=196 ),
               dict( iso3166_1_alpha_2='LC', name='Santa Lúcia', preferred_order=197 ),
               dict( iso3166_1_alpha_2='KN', name='São Cristóvão e Névis (Saint Kitts e Nevis)', preferred_order=198 ),
               dict( iso3166_1_alpha_2='ST', name='São Tomé e Príncipe', preferred_order=199 ),
               dict( iso3166_1_alpha_2='VC', name='São Vicente e Granadinas', preferred_order=200 ),
               dict( iso3166_1_alpha_2='SN', name='Senegal', preferred_order=201 ),
               dict( iso3166_1_alpha_2='SL', name='Serra Leoa', preferred_order=202 ),
               dict( iso3166_1_alpha_2='RS', name='Sérvia', preferred_order=203 ),
               dict( iso3166_1_alpha_2='SC', name='Seychelles', preferred_order=204 ),
               dict( iso3166_1_alpha_2='SG', name='Singapura', preferred_order=205 ),
               dict( iso3166_1_alpha_2='SY', name='Síria', preferred_order=206 ),
               dict( iso3166_1_alpha_2='SO', name='Somália', preferred_order=207 ),
               dict( iso3166_1_alpha_2='LK', name='Sri Lanka', preferred_order=208 ),
               dict( iso3166_1_alpha_2='SZ', name='Suazilândia', preferred_order=209 ),
               dict( iso3166_1_alpha_2='SD', name='Sudão', preferred_order=210 ),
               dict( iso3166_1_alpha_2='SE', name='Suécia', preferred_order=211 ),
               dict( iso3166_1_alpha_2='CH', name='Suíça', preferred_order=212 ),
               dict( iso3166_1_alpha_2='SR', name='Suriname', preferred_order=213 ),
               dict( iso3166_1_alpha_2='SJ', name='Svalbard e Jan Mayen', preferred_order=214 ),
               dict( iso3166_1_alpha_2='TH', name='Tailândia', preferred_order=215 ),
               dict( iso3166_1_alpha_2='TW', name='Taiwan', preferred_order=216 ),
               dict( iso3166_1_alpha_2='TJ', name='Tajiquistão', preferred_order=217 ),
               dict( iso3166_1_alpha_2='TZ', name='Tanzânia', preferred_order=218 ),
               dict( iso3166_1_alpha_2='TF', name='Terras Austrais e Antárticas Francesas (TAAF)', preferred_order=219 ),
               dict( iso3166_1_alpha_2='IO', name='Território Britânico do Oceano Índico', preferred_order=220 ),
               dict( iso3166_1_alpha_2='TL', name='Timor-Leste', preferred_order=221 ),
               dict( iso3166_1_alpha_2='TG', name='Togo', preferred_order=222 ),
               dict( iso3166_1_alpha_2='TO', name='Tonga', preferred_order=223 ),
               dict( iso3166_1_alpha_2='TK', name='Toquelau', preferred_order=224 ),
               dict( iso3166_1_alpha_2='TT', name='Trindade e Tobago', preferred_order=225 ),
               dict( iso3166_1_alpha_2='TN', name='Tunísia', preferred_order=226 ),
               dict( iso3166_1_alpha_2='TC', name='Turks e Caicos', preferred_order=227 ),
               dict( iso3166_1_alpha_2='TM', name='Turquemenistão', preferred_order=228 ),
               dict( iso3166_1_alpha_2='TR', name='Turquia', preferred_order=229 ),
               dict( iso3166_1_alpha_2='TV', name='Tuvalu', preferred_order=230 ),
               dict( iso3166_1_alpha_2='UA', name='Ucrânia', preferred_order=231 ),
               dict( iso3166_1_alpha_2='UG', name='Uganda', preferred_order=232 ),
               dict( iso3166_1_alpha_2='UY', name='Uruguai', preferred_order=233 ),
               dict( iso3166_1_alpha_2='UZ', name='Usbequistão', preferred_order=234 ),
               dict( iso3166_1_alpha_2='VU', name='Vanuatu', preferred_order=235 ),
               dict( iso3166_1_alpha_2='VA', name='Vaticano', preferred_order=236 ),
               dict( iso3166_1_alpha_2='VE', name='Venezuela', preferred_order=237 ),
               dict( iso3166_1_alpha_2='VN', name='Vietnam', preferred_order=238 ),
               dict( iso3166_1_alpha_2='VI', name='Virgens Americanas, Ilhas', preferred_order=239 ),
               dict( iso3166_1_alpha_2='VG', name='Virgens Britânicas, Ilhas', preferred_order=240 ),
               dict( iso3166_1_alpha_2='WF', name='Wallis e Futuna', preferred_order=241 ),
               dict( iso3166_1_alpha_2='ZM', name='Zâmbia', preferred_order=242 ),
               dict( iso3166_1_alpha_2='ZW', name='Zimbabwe', preferred_order=243 ),
    ]
    for v in values:
        c_model.insert( v )
    # country_region
    cr_model = db_tables.get_table_model( 'country_region' )
    values = [ dict( iso3166_1_alpha_2='PT', name='Continente', nuts_code='1', preferred_order=1 ),
               dict( iso3166_1_alpha_2='PT', name='Região Autónoma dos Açores', nuts_code='2', preferred_order=2 ),
               dict( iso3166_1_alpha_2='PT', name='Região Autónoma da Madeira', nuts_code='3', preferred_order=3 ),
    ]
    for v in values:
        q_sql = (db.country.iso3166_1_alpha_2 == v[ 'iso3166_1_alpha_2' ])
        c = c_model.select( q_sql ).first()
        del v[ 'iso3166_1_alpha_2' ]
        v[ 'country_id' ] = c.id
        cr_model.insert( v )
    # district
    db.commit()
    d_model = db_tables.get_table_model( 'district' )
    values = [ dict( iso3166_1_alpha_2='PT', name='Aveiro' ),
               dict( iso3166_1_alpha_2='PT', name='Beja' ),
               dict( iso3166_1_alpha_2='PT', name='Braga' ),
               dict( iso3166_1_alpha_2='PT', name='Bragança' ),
               dict( iso3166_1_alpha_2='PT', name='Castelo Branco' ),
               dict( iso3166_1_alpha_2='PT', name='Coimbra' ),
               dict( iso3166_1_alpha_2='PT', name='Évora' ),
               dict( iso3166_1_alpha_2='PT', name='Faro' ),
               dict( iso3166_1_alpha_2='PT', name='Guarda' ),
               dict( iso3166_1_alpha_2='PT', name='Ilha da Graciosa' ),
               dict( iso3166_1_alpha_2='PT', name='Ilha da Madeira' ),
               dict( iso3166_1_alpha_2='PT', name='Ilha das Flores' ),
               dict( iso3166_1_alpha_2='PT', name='Ilha de Porto Santo' ),
               dict( iso3166_1_alpha_2='PT', name='Ilha de Santa Maria' ),
               dict( iso3166_1_alpha_2='PT', name='Ilha de São Jorge' ),
               dict( iso3166_1_alpha_2='PT', name='Ilha de São Miguel' ),
               dict( iso3166_1_alpha_2='PT', name='Ilha do Corvo' ),
               dict( iso3166_1_alpha_2='PT', name='Ilha do Faial' ),
               dict( iso3166_1_alpha_2='PT', name='Ilha do Pico' ),
               dict( iso3166_1_alpha_2='PT', name='Ilha Terceira' ),
               dict( iso3166_1_alpha_2='PT', name='Leiria' ),
               dict( iso3166_1_alpha_2='PT', name='Lisboa' ),
               dict( iso3166_1_alpha_2='PT', name='Portalegre' ),
               dict( iso3166_1_alpha_2='PT', name='Porto' ),
               dict( iso3166_1_alpha_2='PT', name='Santarém' ),
               dict( iso3166_1_alpha_2='PT', name='Setúbal' ),
               dict( iso3166_1_alpha_2='PT', name='Viana do Castelo' ),
               dict( iso3166_1_alpha_2='PT', name='Vila Real' ),
               dict( iso3166_1_alpha_2='PT', name='Viseu' ),
    ]
    for v in values:
        q_sql = (db.country.iso3166_1_alpha_2 == v[ 'iso3166_1_alpha_2' ])
        c = c_model.select( q_sql ).first()
        del v[ 'iso3166_1_alpha_2' ]
        v[ 'country_id' ] = c.id
        q_sql = (db.country_region.country_id == c.id)
        if v[ 'name' ] == 'Ilha da Madeira':
            q_sql &= (db.country_region.nuts_code == '3')
        elif v[ 'name' ].startswith( 'Ilha ' ):
            q_sql &= (db.country_region.nuts_code == '2')
        else:
            q_sql &= (db.country_region.nuts_code == '1')
        cr = cr_model.select( q_sql ).first()
        term.printDebug( 'cr: %s' % repr( cr ) )
        v[ 'country_region_id' ] = cr.id
        d_model.insert( v, print_query=True )


def populate_home_page():
    T = current.T
    from m16e.db import db_tables
    p_model = db_tables.get_table_model( 'page' )
    ts = DT.now()
    p_id = p_model.insert( dict( name='Home',
                                 tagname='home',
                                 title=T( 'Welcome to Chirico CMS' ),
                                 url_c='default',
                                 url_f='index',
                                 aside_position=db_sets.PANEL_RIGHT,
                                 aside_title=T( 'News' ),
                                 aside_title_en='News',
                                 colspan=3,
                                 rowspan=1,
                                 last_modified_by=1,
                                 page_timestamp=ts,
                                 main_panel_cols=2,
                                 aside_panel_cols=1 ) )
    b_model = db_tables.get_table_model( 'block' )
    txt = '''# %(h1)s

%(p)s

    '''
    h1 = 'Welcome to ChiricoCMS'
    p = 'Once authenticated, click on the top left icon of this panel to edit content.'
    b_model.insert( dict( name='Home main panel',
                          description='Home main panel',
                          page_id=p_id,
                          container=db_sets.BLOCK_CONTAINER_MAIN,
                          blk_order=1,
                          body=txt % dict( h1=T( h1 ), p=T( p ) ),
                          body_en=txt % dict( h1=h1, p=p ),
                          created_on=ts,
                          created_by=1,
                          last_modified_by=1,
                          colspan=2,
                          rowspan=1 ) )
    h1 = 'ChiricoCMS is up'
    p = 'Our site is up and running.\n[+[timestamp]+]'
    b_model.insert( dict( name='News panel',
                          description='News panel',
                          page_id=p_id,
                          container=db_sets.BLOCK_CONTAINER_ASIDE,
                          blk_order=1,
                          body=txt % dict( h1=T( h1 ), p=T( p ) ),
                          body_en=txt % dict( h1=h1, p=p ),
                          created_on=ts,
                          created_by=1,
                          last_modified_by=1,
                          colspan=2,
                          rowspan=1 ) )


def populate_aux_pages():
    T = current.T
    from m16e.db import db_tables
    p_model = db_tables.get_table_model( 'page' )
    ts = DT.now()
    # /about
    p_id = p_model.insert( dict( name='About',
                                 tagname='about',
                                 title=T( 'About us' ),
                                 url_c='about',
                                 url_f='index',
                                 colspan=1,
                                 rowspan=1,
                                 last_modified_by=1,
                                 page_timestamp=ts,
                                 main_panel_cols=1,
                                 aside_panel_cols=1 ) )
    b_model = db_tables.get_table_model( 'block' )
    txt = '''# %(h1)s

%(p)s

    '''
    h1 = 'About us'
    p = 'This is some text describing who we are'
    b_model.insert( dict( name='About panel',
                          description='About panel',
                          page_id=p_id,
                          container=db_sets.BLOCK_CONTAINER_MAIN,
                          blk_order=1,
                          body=txt % dict( h1=T( h1 ), p=T( p ) ),
                          body_en=txt % dict( h1=h1, p=p ),
                          created_on=ts,
                          created_by=1,
                          last_modified_by=1,
                          colspan=2,
                          rowspan=1 ) )
    # /contacts
    p_id = p_model.insert( dict( name='Contacts',
                                 tagname='contacts',
                                 title=T( 'Contacts' ),
                                 url_c='contacts',
                                 url_f='index',
                                 colspan=1,
                                 rowspan=1,
                                 last_modified_by=1,
                                 page_timestamp=ts,
                                 main_panel_cols=1,
                                 aside_panel_cols=1 ) )
    h1 = 'Contacts'
    p = '- E-mail: mail@example.com\n- Address: \n'
    b_model.insert( dict( name='Contacts',
                          description='Contacts panel',
                          page_id=p_id,
                          container=db_sets.BLOCK_CONTAINER_MAIN,
                          blk_order=1,
                          body=txt % dict( h1=T( h1 ), p=T( p ) ),
                          body_en=txt % dict( h1=h1, p=p ),
                          created_on=ts,
                          created_by=1,
                          last_modified_by=1,
                          colspan=1,
                          rowspan=1 ) )
    # /terms_of_use
    p_id = p_model.insert( dict( name='Terms of use',
                                 tagname='terms_of_use',
                                 title=T( 'Terms of use' ),
                                 url_c='about',
                                 url_f='terms_of_use',
                                 colspan=1,
                                 rowspan=1,
                                 last_modified_by=1,
                                 page_timestamp=ts,
                                 main_panel_cols=1,
                                 aside_panel_cols=1 ) )
    h1 = 'Terms of use'
    p = 'In order to use this site you must agree with theese terms.\n'
    b_model.insert( dict( name='Terms of use',
                          description='Terms of use panel',
                          page_id=p_id,
                          container=db_sets.BLOCK_CONTAINER_MAIN,
                          blk_order=1,
                          body=txt % dict( h1=T( h1 ), p=T( p ) ),
                          body_en=txt % dict( h1=h1, p=p ),
                          created_on=ts,
                          created_by=1,
                          last_modified_by=1,
                          colspan=1,
                          rowspan=1 ) )


def populate_pages():
    populate_home_page()
    populate_aux_pages()


def populate():
    from m16e.db import db_tables
    import m16e.db.list_of_tables
    import chirico.db.list_of_tables
    import forum_threads.db.list_of_tables
    db_tables.register_table_list( db, table_list=m16e.db.list_of_tables.TABLE_LIST )
    db_tables.register_table_list( db, table_list=chirico.db.list_of_tables.TABLE_LIST )
    db_tables.register_table_list( db, table_list=forum_threads.db.list_of_tables.TABLE_LIST )

    populate_users()
    populate_mime_types()
    populate_types()
    populate_pages()
    populate_countries()


def initdb():
    init_auth()
    init_company_info()
    init_app_theme()
    init_country()
    init_country_region()
    init_district()

    init_attach_type()
    init_mime_type()
    init_unit_type()
    init_mime_type()
    init_long_task()
    init_thread_status()
    init_thread_type()

    init_page()
    init_mime_type_ext()
    init_attach()
    init_app_config()
    init_block()
    init_block_attach()
    init_mail_queue()
    init_mail_recipient()
    init_page_log()
    init_shared_run()
    init_thread()
    init_thread_attach()
    init_thread_msg()
    init_thread_msg_attach()
    init_thread_subscriber()
    init_thread_vote()
    init_user_message()
    db.commit()

    populate()


