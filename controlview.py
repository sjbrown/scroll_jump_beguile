from utils import *
from objects import SimpleSprite
import pygame
from pygame.locals import *
import data

uprofile = data.userProfile
#font = pygame.font.Font(None, 15)

#-----------------------------------------------------------------------------
class StrSprite( pygame.sprite.Sprite ):

	def __init__(self, theString, size=0):
		pygame.sprite.Sprite.__init__(self)
		if size == 0:
			self.image = data.smallStringPngs[theString]
		else:
			self.image = data.stringPngs[theString]
		self.rect = self.image.get_rect()

#-----------------------------------------------------------------------------
def BlitOnCenter( img1, img2 ):
	def getDestCoords( srcRect, destRect ):
		x = srcRect.width/2 - destRect.width/2
		y = srcRect.height/2 - destRect.height/2
		return (x,y)

	destCoords = getDestCoords( img1.get_rect(), img2.get_rect() )
	img1.blit( img2, destCoords )


#-----------------------------------------------------------------------------
class ControlView:
	def __init__(self, bgMangr, musicMangr):
		self.bgMangr = bgMangr
		self.isDone = 0

		self.neutralGroup = pygame.sprite.RenderUpdates()

		self.listenKeys = {
		 K_RETURN: self.Start,
		 K_SPACE: self.Start,
		}

		self.upString = StrSprite('up')
		self.rightString = StrSprite('right')
		self.downString = StrSprite('down')
		self.leftString = StrSprite('left')
		self.jumpString = StrSprite('jump')
		self.fireString = StrSprite('fire')
		self.upButton = SimpleSprite( 'control_button' )
		self.rightButton = SimpleSprite( 'control_button' )
		self.downButton = SimpleSprite( 'control_button' )
		self.leftButton = SimpleSprite( 'control_button' )
		self.jumpButton = SimpleSprite( 'control_button' )
		self.fireButton = SimpleSprite( 'control_button' )

		self.sprites = [
		 StrSprite('Press SPACE to start', size=1),
		 self.upButton,
		 self.rightButton,
		 self.downButton,
		 self.leftButton,
		 self.jumpButton,
		 self.fireButton,
		 self.upString,
		 self.rightString,
		 self.downString,
		 self.leftString,
		 self.jumpString,
		 self.fireString,
		]

		for s in self.sprites:
			self.neutralGroup.add( s )

		screenRect = bgMangr.screen.get_rect()

		self.sprites[0].rect.midbottom = screenRect.midbottom

		dirCenter = (screenRect.right - (64*3), screenRect.centery)
		self.upButton.rect.center   = ( dirCenter[0], dirCenter[1]-128 )
		self.rightButton.rect.center= ( dirCenter[0]+64, dirCenter[1] )
		self.downButton.rect.center = ( dirCenter[0], dirCenter[1]+128 )
		self.leftButton.rect.center = ( dirCenter[0]-64, dirCenter[1] )
		self.upString.rect.midbottom = self.upButton.rect.midtop
		self.rightString.rect.midleft = self.rightButton.rect.midright
		self.downString.rect.midtop = self.downButton.rect.midbottom
		self.leftString.rect.midright = self.leftButton.rect.midleft

		actionCenter = (screenRect.left + (64*3), screenRect.centery)
		self.jumpButton.rect.center= actionCenter[0]-64,actionCenter[1]
		self.fireButton.rect.center= actionCenter[0]+64,actionCenter[1]
		self.jumpString.rect.midtop = self.jumpButton.rect.midbottom
		self.fireString.rect.midtop = self.fireButton.rect.midbottom

		color = (0,0,0)

		#NOTE: little ugly hack here [2:]
		fontImg = data.smallStringPngs[uprofile['up'][2:]]
		self.upButton.image = self.upButton.image.convert_alpha()
		BlitOnCenter( self.upButton.image, fontImg )

		fontImg = data.smallStringPngs[uprofile['right'][2:]]
		self.rightButton.image = self.rightButton.image.convert_alpha()
		BlitOnCenter( self.rightButton.image, fontImg )

		fontImg = data.smallStringPngs[uprofile['down'][2:]]
		self.downButton.image = self.downButton.image.convert_alpha()
		BlitOnCenter( self.downButton.image, fontImg )

		fontImg = data.smallStringPngs[uprofile['left'][2:]]
		self.leftButton.image = self.leftButton.image.convert_alpha()
		BlitOnCenter( self.leftButton.image, fontImg )

		fontImg = data.smallStringPngs[uprofile['jump'][2:]]
		self.jumpButton.image = self.jumpButton.image.convert_alpha()
		BlitOnCenter( self.jumpButton.image, fontImg )

		fontImg = data.smallStringPngs[uprofile['fire'][2:]]
		self.fireButton.image = self.fireButton.image.convert_alpha()
		BlitOnCenter( self.fireButton.image, fontImg )


	#---------------------------------------------------------------------
	def Start( self ):
		self.isDone = 1
		from level1 import GameLevel
		self.replacementDisplayerClass = GameLevel
		print "FINISHED"


	#---------------------------------------------------------------------
	def SignalKey( self, event, remainingEvents ):
		if self.listenKeys.has_key( event.key ) \
		   and event.type == KEYUP:
			self.listenKeys[event.key]()

	#---------------------------------------------------------------------
	def Click( self, pos ):
		pass
		
	#---------------------------------------------------------------------
	def DoGraphics( self, screen, display, timeChange ):
		self.neutralGroup.clear( screen, self.bgMangr.GetBgSurface )

		self.neutralGroup.update( timeChange )

		changedRects =  self.neutralGroup.draw(screen)
		display.update( changedRects )

