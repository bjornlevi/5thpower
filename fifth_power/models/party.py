#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Party:
	
	def __init__(self, name, short_name):
		self.name = name
		self.short_name = short_name

	def get_current_members(self):
		return None

	def get_members_for_setting(self, setting):
		return None

	def get_all_members(self):
		return None

	def get_settings(self):
		return None

	def save(self):
		#check if exists
			#update
		#else
			#insert
		pass

	def to_json(self):
		return self.__dict__