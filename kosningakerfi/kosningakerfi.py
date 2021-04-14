# -*- coding: utf-8 -*-

from random import randint
from string import ascii_letters

def reikna(atkvaedi, fjoldi_fulltrua):
	#atkvæði eru á forminu {flokkur1: fjöldi atkvæða fyrir flokk1, flokkur2: fjöldi atkvæða ..., ...}
	#fjoldi_fulltrua: heildarfjöldi fulltrúa fyrir kjördæmið
	atkvaedi_kjordaemi = sum([atkvaedi[f] for f in atkvaedi])
	nidurstodur = {}
	for f in atkvaedi:
		hlutfall = 1.0 * fjoldi_fulltrua * atkvaedi[f]/atkvaedi_kjordaemi
		nidurstodur[f] = [int(hlutfall), hlutfall-int(hlutfall)]
	return nidurstodur


kjordaemi = {
	'RN': [9,2],
	'RS': [9,2],
	'SV': [11,2],
	'SU': [9,1],
	'NV': [7,1],
	'NA': [9,1]}

class Flokkur:
	def __init__(self, bokstafur):
		self.bokstafur = bokstafur #ex. 'a'
		self.atkvaedi = {} #{kjördæmi1: fjöldi atkvæða í kjördæmi, kjördæmi2: fjöldi ..., ...}

	def gefa_atkvaedi(self, kjordaemi, atkvaedi):
		self.atkvaedi[kjordaemi] = atkvaedi #kjördæmi = 'RN', atkvaedi = 123

class Kosningar:
	def __init__(self, flokkar, kjordaemi):
		self.flokkar = flokkar #[Flokkur('a'), Flokkur('b'), ...]
		self.kjordaemi = kjordaemi #{'RN': [9,2], 'SU': [9,1], ...}. [fjöldi kjördæmafulltrúa, fjöldi jöfnunarmanna]

	def get_fjoldi_fulltrua(self, kjordaemi):
		return self.kjordaemi[kjordaemi][0]

	def get_fjoldi_jofnun(self, kjordaemi):
		return self.kjordaemi[kjordaemi][1]

	def reikna_kjordaemi(self, kjordaemi):
		#ex. kjordaemi = 'RN'
		#fjöldi atkvæða í kjördæmi
		fj_atkvaeda = 0
		for f in self.flokkar:
			try:
				fj_atkvaeda += f.atkvaedi[kjordaemi]
			except:
				#flokkur ekki með atkvæði í kjördæmi
				pass
		#búa til heildar- og hlutatölur fyrir flokka
		nidurstodur = {}
		for f in self.flokkar:
			try:
				fulltrua_hlutfall = self.get_fjoldi_fulltrua(kjordaemi) * 1.0 * f.atkvaedi[kjordaemi]/fj_atkvaeda
				nidurstodur[f.bokstafur] = [int(fulltrua_hlutfall), fulltrua_hlutfall-int(fulltrua_hlutfall)]
			except:
				#flokkur ekki í framboði í þessu kjördæmi
				pass
		return nidurstodur


#flokkar = [a for a in ascii_letters[0:randint(1,len(ascii_letters)/2-1)]]
flokkar = [Flokkur(a) for a in ascii_letters[0:4]]

kosningar = Kosningar(flokkar, kjordaemi)

for k in kosningar.kjordaemi:
	for f in kosningar.flokkar:
		if randint(0,20) == 0:
			#flokkur ekki í framboði í þessu kjördæmi
			pass
		else:
			#handahófskennt val á fjölda atkvæða fyrir viðkomandi flokk
			a = randint(0,50000)
			f.gefa_atkvaedi(k,a)

print(u"Útkoma atkvæðagreiðslu")
for f in kosningar.flokkar:
	print(f.bokstafur)
	print(f.atkvaedi)

class Nidurstodur:
	def __init__(self, kjordaemi, flokkar):
		self.nidurstodur = {}
		for k in kjordaemi:
			self.nidurstodur[k] = {}
			for f in flokkar:
				self.nidurstodur[k][f] = 0



kosninga_nidurstodur = {}

nidurstodur = Nidurstodur(kosningar.kjordaemi, kosningar.flokkar)

#úthluta kjördæmasætum
for k in kosningar.kjordaemi:
	#ex. k = 'RN'
	kjordaemi_nidurstodur = kosningar.reikna_kjordaemi(k)
	print(kjordaemi_nidurstodur)


