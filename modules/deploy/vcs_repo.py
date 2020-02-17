#! /usr/bin/python
# coding=utf-8


class VcsRepo( object ):

    def __init__( self, current_app ):
        self.current_app = current_app
        self.local_status = None
        self.local_status_resumed = None
        self.remote_status = None
        self.remote_status_resumed = None
        self.version = None
        self.version_date = None
        self.tip = None
        self.changeset = None
        self.refreshed = False


    def refresh_remote(self):
        pass


    def refresh_local(self):
        pass


    def get_format_status_header( self, style='line' ):
        return None


    def format_status( self, style='line' ):
        return None


