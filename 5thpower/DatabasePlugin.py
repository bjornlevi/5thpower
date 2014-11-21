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
        self.bus.subscribe("get-data", self.get_data)
        self.bus.subscribe("db-save", self.save_it)
        self.bus.subscribe("db-update", self.update_it)
        self.bus.subscribe("db-delete", self.delete_it)
        self.bus.subscribe("db-get", self.get_it)
        self.bus.subscribe("db-getwhere", self.get_what)
        self.bus.subscribe("db-getall", self.get_all)

    def stop(self):
        self.bus.log('Stopping down DB access')
        self.bus.unsubscribe("get-data", self.get_data)
        self.bus.unsubscribe("db-save", self.save_it)
        self.bus.unsubscribe("db-update", self.update_it)
        self.bus.unsubscribe("db-delete", self.delete_it)
        self.bus.unsubscribe("db-get", self.get_it)
        self.bus.unsubscribe("db-getwhere", self.get_what)
        self.bus.unsubscribe("db-getall", self.get_all)

    @cherrypy.tools.json_out()
    def get_data(self, vote_id):
        return self.db.get_data(vote_id)

    @cherrypy.tools.json_out()
    def save_it(self, entity):
        return self.db.save(entity)

    @cherrypy.tools.json_out()
    def update_it(self, update_id, data):
        return self.db.update(update_id, data)

    @cherrypy.tools.json_out()
    def delete_it(self, entity):
        return self.db.delete(entity)

    @cherrypy.tools.json_out()
    def get_it(self, entity):
        return self.db.get(entity) 

    @cherrypy.tools.json_out()
    def get_what(self, entity):
        return self.db.get_where(entity)  

    @cherrypy.tools.json_out()
    def get_all(self):
        return self.db.get_all()                                