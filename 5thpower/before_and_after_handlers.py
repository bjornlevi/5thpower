import cherrypy
import uuid

def before_submit():
	try:
		cherrypy.request.json["vote_id_from"] = int(cherrypy.request.json["vote_id_from"])
		cherrypy.request.json["vote_id_to"] = int(cherrypy.request.json["vote_id_to"])
	except:
		cherrypy.request.json["vote_id_from"] = 0
		cherrypy.request.json["vote_id_to"] = 0

def after_submit():
	pass

def before_update():
	pass

def after_update():
	pass

def before_delete():
	pass

def after_delete():
	pass

def before_get():
	pass

def after_get():
	pass

def before_get_where():
	pass

def after_get_where():
	pass

def before_get_all():
	pass

def after_get_all():
	pass
