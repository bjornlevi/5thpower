#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cherrypy
import simplejson
from DatabasePlugin import DatabasePlugin

from db import DB
import input_validation
import before_and_after_handlers as handlers

def CORS():
	cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
	#cherrypy.response.headers["Access-Control-Request-Headers"] = "x-requested-with"
	#cherrypy.response.headers["Access-Control-Allow-Headers"] = "Origin, x-requested-with, Content-Type, Authorization, Accept, "

def json_fix():
	cherrypy.request.json["fix"] = "fix"

#handlers
cherrypy.tools.validate_and = cherrypy.Tool('before_request_body', json_fix, priority=1)
cherrypy.tools.validate_and = cherrypy.Tool('before_handler', input_validation.validate_and, priority=51)
cherrypy.tools.validate_or = cherrypy.Tool('before_handler', input_validation.validate_or, priority=51)
cherrypy.tools.before_submit = cherrypy.Tool('before_handler', handlers.before_submit, priority=52)
cherrypy.tools.after_submit = cherrypy.Tool('before_finalize', handlers.after_submit, priority=99)
cherrypy.tools.before_update = cherrypy.Tool('before_handler', handlers.before_update, priority=52)
cherrypy.tools.after_update = cherrypy.Tool('before_finalize', handlers.after_update, priority=99)
cherrypy.tools.before_delete = cherrypy.Tool('before_handler', handlers.before_delete, priority=52)
cherrypy.tools.after_delete = cherrypy.Tool('before_finalize', handlers.after_delete, priority=99)
cherrypy.tools.before_get = cherrypy.Tool('before_handler', handlers.before_get, priority=52)
cherrypy.tools.after_get = cherrypy.Tool('before_finalize', handlers.after_get, priority=99)
cherrypy.tools.before_get_where = cherrypy.Tool('before_handler', handlers.before_get_where, priority=52)
cherrypy.tools.after_get_where = cherrypy.Tool('before_finalize', handlers.after_get_where, priority=99)
cherrypy.tools.before_get_all = cherrypy.Tool('before_handler', handlers.before_get_all, priority=52)
cherrypy.tools.after_get_all = cherrypy.Tool('before_finalize', handlers.after_get_all, priority=99)

cherrypy.tools.CORS = cherrypy.Tool('before_finalize', CORS)

class Controller(object):
	@cherrypy.expose
	@cherrypy.tools.json_in()
	@cherrypy.tools.json_out()
	@cherrypy.tools.validate_and(data_structure=input_validation.submit)
	@cherrypy.tools.before_submit()
	@cherrypy.tools.after_submit()
	@cherrypy.tools.allow(methods=['POST', 'OPTIONS'])
	def submit(self):
		try:
			ids = []
			for vote_id in range(cherrypy.request.json["vote_id_from"], cherrypy.request.json["vote_id_to"]):
				ids.append(cherrypy.engine.publish('get-data', vote_id))
			return ids
		except:
			return

	@cherrypy.expose
	@cherrypy.tools.json_in()
	@cherrypy.tools.json_out()
	@cherrypy.tools.validate_and(data_structure=input_validation.update)
	@cherrypy.tools.before_update()
	@cherrypy.tools.after_update()
	@cherrypy.tools.allow(methods=['PUT'])
	def update(self):
		update_id = cherrypy.request.json["update_id"]
		update_data = cherrypy.request.json["update_data"]
		return cherrypy.engine.publish('db-update', update_id, update_data)

	@cherrypy.expose
	@cherrypy.tools.json_in()
	@cherrypy.tools.json_out()
	@cherrypy.tools.validate_or(data_structure=input_validation.delete)
	@cherrypy.tools.before_delete()
	@cherrypy.tools.after_delete()
	@cherrypy.tools.allow(methods=['POST'])
	def delete(self):
		return cherrypy.engine.publish('db-delete', cherrypy.request.json)

	@cherrypy.expose
	@cherrypy.tools.json_out()
	@cherrypy.tools.before_get()
	@cherrypy.tools.after_get()
	@cherrypy.tools.gzip(mime_types=["application/json"])
	@cherrypy.tools.allow(methods=['GET'])
	def get(self, _id):
		return cherrypy.engine.publish('db-get', _id)

	@cherrypy.expose
	@cherrypy.tools.json_in()
	@cherrypy.tools.json_out()
	@cherrypy.tools.validate_or(data_structure=input_validation.get_where)
	@cherrypy.tools.before_get_where()
	@cherrypy.tools.after_get_where()
	@cherrypy.tools.gzip(mime_types=["application/json"])
	@cherrypy.tools.allow(methods=['POST'])
	def get_where(self):
		return cherrypy.engine.publish('db-getwhere', cherrypy.request.json)

	@cherrypy.expose
	@cherrypy.tools.json_out()
	@cherrypy.tools.before_get_all()
	@cherrypy.tools.after_get_all()
	@cherrypy.tools.gzip(mime_types=["application/json"])
	@cherrypy.tools.allow(methods=['GET'])
	def get_all(self):
		print cherrypy.request.headers
		return cherrypy.engine.publish('db-getall')

if __name__ == '__main__':
	DatabasePlugin(cherrypy.engine, DB).subscribe()
	cherrypy.config.update(file('server.conf'))
	root = Controller()

	cherrypy.quickstart(root, '/')