# -*- coding: utf-8 -*-

import requests
import xmltodict
from includes import get_mp_commitee_membership_dates, get_commitee_meeting_dates

data = get_mp_commitee_membership_dates(1215)

print data
