from utils import load_png, load_sound
import pygame
from log import log

class UserDict(dict): pass

# DynamicCachingLoader is an **ABSTRACT** class.  It must be inherited
# from and the subclas MUST implement LoadResource( attname )
class DynamicCachingLoader(UserDict):
	def __init__(self):
		self._d = {}
	def __getattr__(self, attname):
		try:
			return self.__dict__[attname]
		except KeyError:
			log.debug( 'loader got key err' )
			try:
				return self._d[attname]
			except KeyError:
				self.LoadResource( attname )
				return self._d[attname]

	def __getitem__(self, key):
		try:
			return self._d[key]
		except KeyError:
			self.LoadResource( key )
			return self._d[key]



class PngLoader(DynamicCachingLoader):
	def LoadResource(self, name):
		self._d[name] = load_png( name +'.png' )

class OggLoader(DynamicCachingLoader):
	def LoadResource(self, name):
		self._d[name] = load_sound( name +'.ogg' )

class StringPngLoader(DynamicCachingLoader):
	def LoadResource(self, name):
		fname = name.replace( ' ', '_' ) + '.png'
		try:
			self._d[name] = load_png( fname )
		except pygame.error:
			font = pygame.font.Font(None, 60) 
			self._d[name] = font.render( name, 1, (255,255,255) )

class SmallStringPngLoader(DynamicCachingLoader):
	def LoadResource(self, name):
		fname = name.replace( ' ', '_' ) + '.png'
		color = (0,0,0)
		try:
			self._d[name] = load_png( fname )
		except pygame.error:
			font = pygame.font.Font(None, 28) 
			self._d[name] = font.render( name, 1, color )

class WeaponIconLoader(DynamicCachingLoader):
	def LoadResource(self, weaponClass ):
		try:
			cName = 'icon_'+ weaponClass.__name__.lower()
			self._d[weaponClass] = load_png( cName +'.png')
		except pygame.error:
			print 'there was a pygame error'
			#make a transparent surface
			img = Surface( (40, 40), SRCALPHA, 32 )
			img.fill( [0,0,0,0] )
			#make a filled circle the color of the weapon
			col = weaponClass().GetColor()
			circle = pygame.draw.circle( img, col, (20,20), 35, 0 )
			#store the surface
			self._d[weaponClass] = img
		except Exception, e:
			log.debug( 'dynamic loader failed '+ str(e) )
			raise e

