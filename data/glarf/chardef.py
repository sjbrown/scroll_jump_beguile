from animations import *
from data.dyn_cache import DynamicCachingLoader
from data.utils import load_png
class PngLoader(DynamicCachingLoader):
	def LoadResource(self, name):
		self._d[name] = load_png( name +'.png', 'glarf' )
pngs = PngLoader()
		
a = {}
b = 'glarf'

#---Rest animation ---

#	 image		attack		vulnerable	dur	offset
a['walk'] = Animation( [
Frame(pngs.glarf19,	None,		None,	2,	[0,0] ),
Frame(pngs.glarf20,	None,		None,	2,	[0,0] ),
Frame(pngs.glarf21,	None,		None,	2,	[0,0] ),
Frame(pngs.glarf22,	None,		None,	2,	[0,0] ),
Frame(pngs.glarf23,	None,		None,	2,	[0,0] ),
Frame(pngs.glarf24,	None,		None,	2,	[0,0] ),
Frame(pngs.glarf25,	None,		None,	2,	[0,0] ),
Frame(pngs.glarf26,	None,		None,	2,	[0,0] ),
Frame(pngs.glarf27,	None,		None,	2,	[0,0] ),
Frame(pngs.glarf28,	None,		None,	2,	[0,0] ),
Frame(pngs.glarf10,	None,		None,	2,	[0,0] ),
Frame(pngs.glarf11,	None,		None,	2,	[0,0] ),
Frame(pngs.glarf12,	None,		None,	2,	[0,0] ),
Frame(pngs.glarf13,	None,		None,	2,	[0,0] ),
Frame(pngs.glarf14,	None,		None,	2,	[0,0] ),
Frame(pngs.glarf15,	None,		None,	2,	[0,0] ),
Frame(pngs.glarf16,	None,		None,	2,	[0,0] ),
Frame(pngs.glarf17,	None,		None,	2,	[0,0] ),
Frame(pngs.glarf18,	None,		None,	2,	[0,0] ),
 ], loop=1 )

#a['prep'] = Animation( [
#Frame(pngs.Gjump01,	None,		None,	1,	[0,0] ),
#], loop=0 )

a['jump'] = Animation( [
Frame(pngs.Gjump01,	None,		None,	1,	[0,0] ),
Frame(pngs.Gjump02,	None,		None,	1,	[0,0] ),
Frame(pngs.Gjump03,	None,		None,	2,	[0,0] ),
Frame(pngs.Gjump04,	None,		None,	2,	[0,0] ),
Frame(pngs.Gjump05,	None,		None,	2,	[0,0] ),
 ], loop=0 )

a['peak'] = Animation( [
Frame(pngs.Gjump06,	None,		None,	2,	[0,0] ),
 ], loop=0 )

a['fall'] = Animation( [
Frame(pngs.Gjump07,	None,		None,	2,	[0,0] ),
Frame(pngs.Gjump08,	None,		None,	2,	[0,0] ),
Frame(pngs.Gjump09,	None,		None,	2,	[0,0] ),
Frame(pngs.Gjump10,	None,		None,	2,	[0,0] ),
 ], loop=0 )

a['land'] = Animation( [
Frame(pngs.Gjump12,	None,		None,	2,	[0,0] ),
Frame(pngs.Gjump13,	None,		None,	2,	[0,0] ),
Frame(pngs.Gjump14,	None,		None,	2,	[0,0] ),
Frame(pngs.Gjump15,	None,		None,	2,	[0,0] ),
 ], loop=0 )




#---In-Fight animation ---

#	 image		attack		vulnerable	dur	offset
a['rest'] = Animation( [
Frame(pngs.glarf12,	None,		None,	22,	[0,0] ),
Frame(pngs.glarf11,	None,		None,	4,	[0,0] ),
 ], loop=1 )

turnPng1 = pygame.transform.flip( pngs.glarf17, 1, 0 )
turnPng2 = pygame.transform.flip( pngs.glarf18, 1, 0 )
turnPng3 = pygame.transform.flip( pngs.glarf19, 1, 0 )
#	 image		attack		vulnerable	dur	offset
a['turn'] = Animation( [
Frame(turnPng1,	None,		None,	1,	[0,0] ),
Frame(turnPng2,	None,		None,	1,	[0,0] ),
Frame(turnPng3,	None,		None,	2,	[0,0] ),
 ], loop=0 )




#	 image		attack		vulnerable	dur	offset
#a['death'] = Animation( [
#Frame(pngs.attack01,	None,		None,	6,	[0,0] ),
#Frame(pngs.attack02,	None,		None,	6,	[0,0] ),
 #], loop=0 )

#	 image		attack		vulnerable	dur	offset
#a['healthKit'] = Animation( [
#Frame(pngs.heal01,	None,		None,	6,	[0,0] ),
#Frame(pngs.heal02,	None,		None,	6,	[0,0] ),
#Frame(pngs.heal01,	None,		None,	6,	[0,0] ),
 #], loop=0 )

charAnims = AllAnimations( a )

default = a['walk']
walk = a['walk']
rest = a['rest']
turn = a['turn']
#prep = a['jump']
jump = a['jump']
peak = a['peak']
fall = a['fall']
land = a['land']
