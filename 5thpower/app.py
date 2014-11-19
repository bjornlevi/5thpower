#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cherrypy
import simplejson
from scraper import Scraper

class Controller(object):
	@cherrypy.expose
	@cherrypy.tools.allow(methods=['GET'])
	def index(self):
		return """
			<html>
			<body>
				<a href='/thingflokkar'>thingflokkar</a><br/>
				<a href='/thing?type=l&thing=144'>lagafrumvorp</a><br/>
				<a href='/thing?type=afv&thing=144'>thingsalyktanir</a><br/>
				<a href='/atkvaedi'>atkvaedi</a><br/>
				<a href='/maeting'>maeting</a><br/>
			</body>
			</html>
		"""

	@cherrypy.expose
	@cherrypy.tools.json_out()
	@cherrypy.tools.allow(methods=['GET'])
	def thingflokkar(self):
		return Scraper().thingflokkar()

	@cherrypy.expose
	@cherrypy.tools.allow(methods=['GET'])
	def thing(self, type, thing):
		return Scraper().thing(type, thing)

	@cherrypy.expose
	@cherrypy.tools.allow(methods=['GET'])
	def thingmenn(self, thing):
		return Scraper().thingmenn(thing)

	@cherrypy.expose
	@cherrypy.tools.json_out()
	@cherrypy.tools.allow(methods=['GET'])
	def atkvaedi(self):
		return Scraper().get_all_votes()

	@cherrypy.expose
	@cherrypy.tools.json_out()
	@cherrypy.tools.allow(methods=['GET'])
	def fundir(self, thing):
		return Scraper().fundir(thing)

	@cherrypy.expose
	@cherrypy.tools.json_out()
	@cherrypy.tools.allow(methods=['GET'])
	def fundur(self, url):
		return Scraper().fundur(url)

if __name__ == '__main__':
	cherrypy.config.update(file('server.conf'))
	root = Controller()
	cherrypy.quickstart(root, '/')