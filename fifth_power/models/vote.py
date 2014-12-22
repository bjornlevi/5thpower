#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Vote:
	
	def __init__(self, voter, vote, vote_id, setting, phase, date, issue, issue_type):
		self.voter = voter
		self.vote = vote
		self.vote_id = vote_id
		self.setting = setting
		self.phase = phase
		self.date = date
		self.issue_ = issue
		self.issue_type = issue_type

	def save(self):
		#inser
		pass

	def to_json(self):
		return self.__dict__