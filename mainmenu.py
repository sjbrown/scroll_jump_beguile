from objects import *
from utils import *
from pygame.locals import *
import data

uprofile = data.userProfile
gprofile = data.gameProfile

#-----------------------------------------------------------------------------
class MainMenu:
	def __init__(self, bgMangr, musicMangr):
		self.bgMangr = bgMangr
		self.isDone = 0

		musicMangr.PlaySong( data.oggs['glarf_intro'] )

		self.neutralGroup = pygame.sprite.RenderUpdates()
		#self.effectGroup  = pygame.sprite.RenderUpdates()

		self.listenKeys = {
		 K_RETURN: self.Start,
		 K_SPACE: self.Start,
		 K_UP: self.UpOrDown,
		 K_DOWN: self.UpOrDown,
		}

		self.options = [
		 SimpleSprite( 'menu_start' ),
		 #SimpleSprite( 'menu_options' ),
		 SimpleSprite( 'menu_quit' ),
		]

		for op in self.options:
			self.neutralGroup.add( op )

		self.options[0].rect.move_ip( 200, 100 )
		self.options[1].rect.move_ip( 200, 200 )

		self.cursor = Superstar( self, (130, 0) )
		self.cursor.rect.centery = self.options[0].rect.centery
		self.neutralGroup.add( self.cursor )


	#---------------------------------------------------------------------
	def SpriteBirth(self, sprite):
		self.idlers.remove( sprite )
		self.neutralGroup.add( sprite )

		self.solids.add( sprite )

	#---------------------------------------------------------------------
	def SpriteDeath(self, sprite):
		if self.resurrect:
			sprite.kill()
			if sprite.Resurrect():
				self.idlers.add( sprite )
		else:
			sprite.kill()

	#---------------------------------------------------------------------
	def Start( self ):
		self.isDone = 1
		if uprofile['firstTime'] == '1':
			from controlview import ControlView 
			self.replacementDisplayerClass = ControlView
			uprofile['firstTime'] = '0'
		else:
			from level1 import GameLevel
			self.replacementDisplayerClass = GameLevel

	#---------------------------------------------------------------------
	def Options( self ):
		raise NotImplemented
		self.isDone = 1
		#self.replacementDisplayerClass = OptionsScreen

	#---------------------------------------------------------------------
	def Quit( self ):
		self.isDone = 1
		self.replacementDisplayerClass = QuitScreen


	#---------------------------------------------------------------------
	def UpOrDown( self ):
		if self.listenKeys[K_RETURN] == self.Quit:
			self.listenKeys[K_RETURN] = self.Start
			self.listenKeys[K_SPACE] = self.Start
			self.cursor.rect.centery = self.options[0].rect.centery
		else:
			self.listenKeys[K_RETURN] = self.Quit
			self.listenKeys[K_SPACE] = self.Quit
			self.cursor.rect.centery = self.options[1].rect.centery

		self.cursor.rect.move_ip( 0, 10 )



	#---------------------------------------------------------------------
	def SignalKey( self, event, remainingEvents ):
		if self.listenKeys.has_key( event.key ) \
		   and event.type == KEYUP:
			self.listenKeys[event.key]()
			#print 'calling ', self.listenKeys[event.key]

	#---------------------------------------------------------------------
	def Click( self, pos ):
		pass
	#---------------------------------------------------------------------
	def MouseOver( self, event ):
		pass
		
	#---------------------------------------------------------------------
	def DoGraphics( self, screen, display, timeChange ):
		self.neutralGroup.clear( screen, self.bgMangr.GetBgSurface )
		#self.effectGroup.clear( screen, self.bgMangr.GetBgSurface )

		self.neutralGroup.update( timeChange )
		#self.effectGroup.update( )

		changedRects =  self.neutralGroup.draw(screen)
		#changedRects += self.effectGroup.draw(screen)
		display.update( changedRects )


oneDay = 60*60*24
#-----------------------------------------------------------------------------
class QuitScreen(MainMenu):
	#---------------------------------------------------------------------
	def __init__(self, bgMangr, musicMangr):
		self.bgMangr = bgMangr
		self.isDone = 0

		#default to 100 days old
		self.ageOfGraphic = oneDay*100

		self.neutralGroup = pygame.sprite.RenderUpdates()
		self.byeFile = os.path.join( uprofile['prefDir'], 'goodbye.png' )

		try:
			image = pygame.image.load(self.byeFile)
			image = image.convert()
			self.byeSprite = pygame.sprite.Sprite()
			self.byeSprite.image = image
			self.byeSprite.rect = image.get_rect()
			import time, stat
			lastModified = os.lstat(self.byeFile)[stat.ST_MTIME]
			self.ageOfGraphic = time.time() - lastModified
		except:
			self.byeSprite = SimpleSprite( 'goodbye' )


		self.byeSprite.rect.center = bgMangr.screen.get_rect().center

		self.textSprite = pygame.sprite.Sprite()
		self.textSprite.image = data.stringPngs['Press any key to exit']
		self.textSprite.rect = self.textSprite.image.get_rect()
		self.textSprite.rect.midbottom = bgMangr.screen.get_rect().midbottom

		self.neutralGroup.add( self.byeSprite )
		self.neutralGroup.add( self.textSprite )


	#---------------------------------------------------------------------
	def SignalKey( self, event, remainingEvents ):
		self.isDone = 1
		
	#---------------------------------------------------------------------
	def Click( self, pos ):
		import webbrowser
		webbrowser.open( gprofile['homeURL'], 1, 1 )
	#---------------------------------------------------------------------
	def MouseOver( self, event ):
		pass

	#---------------------------------------------------------------------
	def DoGraphics( self, screen, display, timeChange ):
		self.neutralGroup.clear( screen, self.bgMangr.GetBgSurface )

		self.neutralGroup.update( timeChange )

		changedRects =  self.neutralGroup.draw(screen)
		display.update( changedRects )

		#load the new graphic from the internet
		#NOTE : we do the drawing above so we can toss up a temporary
		#       graphic while this guy is downloading
		if uprofile['online'] == '1' \
		 and self.ageOfGraphic > oneDay:
			self.ageOfGraphic = 0
			try:
				urllib.urlretrieve( 
				         gprofile['goodbyeURL'],
				         self.byeFile
				                  )
			except:
				print "HELLS!  couldn't download goodbye png"
