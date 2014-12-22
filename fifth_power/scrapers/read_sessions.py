#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient, Connection
from utility import get_sessions

connection_name = "althingi"
session_collection = "sessions"
connection = Connection()
db = connection[connection_name]

def collect_sessions():
	session_info = get_sessions()
	return session_info

def get_session(session_nr):
	session_info = get_sessions()
	return [s for session in session_info if session_nr in session.keys()]