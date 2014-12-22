#!/usr/bin/env python
# -*- coding: utf-8 -*-

class MP:
	
	def __init__(self, name, short_name, mp_id, image_url):
		self.name = name
		self.short_name = short_name
		self.mp_id = mp_id
		self.sessions = []
		self.image_url = image_url
		self.deputy = {}

	def add_session(self, session):
		self.sessions.append(session)

	def add_deputy(self, session, deputy_for):
		self.deputy[session] = deputy_for

	def save(self):
		#check if exists
			#update
		#else
			#inser
		pass

	def to_json(self):
		return self.__dict__