#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cherrypy
from cherrypy.process import wspbus, plugins

class DatabasePlugin(plugins.SimplePlugin):
    def __init__(self, bus, db_klass):
        plugins.SimplePlugin.__init__(self, bus)
        self.db = db_klass()

    def start(self):
        self.bus.log('Starting up DB access')
        self.bus.subscribe("get-votes", self.get_votes)
        self.bus.subscribe("get-mps", self.get_mps)
        self.bus.subscribe("get-absents", self.get_absents)
        self.bus.subscribe("get-vote-options", self.get_vote_options)

    def stop(self):
        self.bus.log('Stopping down DB access')
        self.bus.unsubscribe("get-votes", self.get_votes)
        self.bus.subscribe("get-mps", self.get_mps)
        self.bus.subscribe("get-absents", self.get_absents)
        self.bus.subscribe("get-vote-options", self.get_vote_options)

    @cherrypy.tools.json_out()
    def get_votes(self, session):
        return self.db.get_votes(session)

    @cherrypy.tools.json_out()
    def get_mps(self, session):
        return self.db.get_mps(session)

    @cherrypy.tools.json_out()
    def get_absents(self):
        return self.db.get_absents()

    @cherrypy.tools.json_out()
    def get_vote_options(self, session):
        return self.db.get_vote_options(session)                    