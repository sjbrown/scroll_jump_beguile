from animations import *
from data.dyn_cache import DynamicCachingLoader
from data.utils import load_png
class PngLoader(DynamicCachingLoader):
	def LoadResource(self, name):
		self._d[name] = load_png( name +'.png', 'ball' )
pngs = PngLoader()
		
a = {}

#	 image		attack		vulnerable	dur	offset
a['air'] = Animation( [
Frame(pngs.ball01,	None,		None,	9,	[0,0] ),
Frame(pngs.ball02,	None,		None,	6,	[0,0] ),
 ], loop=1 )

#	 image		attack		vulnerable	dur	offset
a['squish'] = Animation( [
Frame(pngs.ballsquish01,	None,		None,	3,	[0,0] ),
Frame(pngs.ballsquish02,	None,		None,	2,	[0,0] ),
 ], loop=0 )

charAnims = AllAnimations( a )

default = a['air']
squish = a['squish']
air = a['air']
