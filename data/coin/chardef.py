from animations import *
from data.dyn_cache import DynamicCachingLoader
from data.utils import load_png
class PngLoader(DynamicCachingLoader):
	def LoadResource(self, name):
		self._d[name] = load_png( name +'.png', 'coin' )
pngs = PngLoader()
		
a = {}

#	 image		attack		vulnerable	dur	offset
a['default'] = Animation( [
Frame(pngs.coin01,	None,		None,	9,	[0,0] ),
Frame(pngs.coin02,	None,		None,	6,	[0,0] ),
 ], loop=1 )


charAnims = AllAnimations( a )

default = a['default']
