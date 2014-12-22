#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cherrypy
import simplejson
from DatabasePlugin import DatabasePlugin

from db import DB
import input_validation
import before_and_after_handlers as handlers

from scrapers import utility

def CORS():
	cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
	#cherrypy.response.headers["Access-Control-Request-Headers"] = "x-requested-with"
	#cherrypy.response.headers["Access-Control-Allow-Headers"] = "Origin, x-requested-with, Content-Type, Authorization, Accept, "

def json_fix():
	cherrypy.request.json["fix"] = "fix"

#handlers
#cherrypy.tools.validate_and = cherrypy.Tool('before_request_body', json_fix, priority=1)
#cherrypy.tools.validate_and = cherrypy.Tool('before_handler', input_validation.validate_and, priority=51)
#cherrypy.tools.after_submit = cherrypy.Tool('before_finalize', handlers.after_submit, priority=99)

cherrypy.tools.CORS = cherrypy.Tool('before_finalize', CORS)

class Controller(object):
	"""
	query options:
	- get_votes(thing) #return all votes for selected thing
	- get_all_things() #return all thing meetings [123, 124, ...]
	- get_current_thing() #return the current/most recent (new one not started) thingmeeting
	- get_mps(thing) #return the mp short names for the selected thing
	- mp_votes(mp, thing) #return the mp votes for the selected thing
	- mp_absents(mp, thing) #return the mp absents for the selected thing
	- total_nr_of_votes() #return the total number of votes
	- total_nr_of_mps() #return the total number of mps
	- thing_statistics(thing) #return common statistics on selected thing
	"""

	@cherrypy.expose
	@cherrypy.tools.json_out()
	@cherrypy.tools.allow(methods=['GET'])
	def get_votes(self, session):
		return cherrypy.engine.publish('get-votes', session)

	@cherrypy.expose
	@cherrypy.tools.json_out()
	@cherrypy.tools.allow(methods=['GET'])
	def get_all_things(self):
		return {'all_things': utility.get_sessions()}

	@cherrypy.expose
	@cherrypy.tools.json_out()
	@cherrypy.tools.allow(methods=['GET'])
	def get_current_thing(self):
		return {'current_thing': max(utility.get_sessions())}

	@cherrypy.expose
	@cherrypy.tools.json_out()
	@cherrypy.tools.allow(methods=['GET'])
	def get_mps(self, session):
		return cherrypy.engine.publish('get-mps', session)

	@cherrypy.expose
	@cherrypy.tools.json_out()
	@cherrypy.tools.allow(methods=['GET'])
	def get_absents(self):
		return cherrypy.engine.publish('get-absents')

	@cherrypy.expose
	@cherrypy.tools.json_out()
	@cherrypy.tools.allow(methods=['GET'])
	def get_vote_options(self, session):
		return cherrypy.engine.publish('get-vote-options', session)		

if __name__ == '__main__':
	DatabasePlugin(cherrypy.engine, DB).subscribe()
	cherrypy.config.update(file('server.conf'))
	root = Controller()

	cherrypy.quickstart(root, '/')