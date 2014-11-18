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
		return {'hello': 'important stuff'}

	@cherrypy.expose
	@cherrypy.tools.allow(methods=['GET'])
	def thing(self, type, thing):
		return Scraper().thing(type, thing)

	@cherrypy.expose
	@cherrypy.tools.json_out()
	@cherrypy.tools.allow(methods=['GET'])
	def atkvaedi(self):
		return {'hello': 'important stuff'}

	@cherrypy.expose
	@cherrypy.tools.json_out()
	@cherrypy.tools.allow(methods=['GET'])
	def maeting(self):
		return {'hello': 'important stuff'}


if __name__ == '__main__':
	cherrypy.config.update(file('server.conf'))
	root = Controller()
	cherrypy.quickstart(root, '/')