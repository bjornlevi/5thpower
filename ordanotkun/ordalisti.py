# -*- coding: utf-8 -*-

import xmltodict
import random

lemmas = []
print('Sæki gögn')
with open('ISLEX_dict/islex_final.xml') as islex:
	doc = xmltodict.parse(islex.read())
	for entry in doc[u'LexicalResource'][u'Lexicon'][u'LexicalEntry']:
		lemmas.append(entry[u'Lemma'][u'feat'][u'@val'])
		
print('Vista orðalista')
with open('ordalisti.txt', 'w') as f:
	f.write("\n".join(lemmas))