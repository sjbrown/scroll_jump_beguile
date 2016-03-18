#!/usr/bin/env python
#Import Modules
import os, pygame, operator, math
from copy import copy
from random import Random
from pygame.locals import *
import data

from anim_widget import AnimatedWidget


from pygame.sprite import Group
from scrollGroup import ScrollSpriteGroup, IdlerSpriteGroup
from utils import *
from physics import *
from scroll_bgmanager import BackgroundManager

FACINGLEFT=1
FACINGRIGHT=0

rng = Random()


#-----------------------------------------------------------------------------
class SimpleSprite(pygame.sprite.Sprite):
	def __init__(self, imgName=None ):
		pygame.sprite.Sprite.__init__(self) #call Sprite initializer
		if imgName:
			self.image = data.pngs[imgName]
			self.rect = self.image.get_rect()
		else:
			self.image = pygame.Surface( (50,50) )
			self.image.fill( (200,0,0) )
			self.rect = self.image.get_rect()
		self.displayRect = self.rect.move(0,0)
	#---------------------------------------------------------------------
	def NotifyDirtyScreen(self, bgMangr ):
		pass
	#---------------------------------------------------------------------
	def NotifyOutOfBounds(self, bounds ):
		pass
		#print "WENT OFF THE MAP"
	#---------------------------------------------------------------------
	def update(self, timeChange=0):
		pass
	#----------------------------------------------------------------------
	def BumpLeft(self, bumpSprite ):
		pass
	#----------------------------------------------------------------------
	def BumpRight(self, bumpSprite ):
		pass
	#----------------------------------------------------------------------
	def BumpTop(self, bumpSprite ):
		pass
	#----------------------------------------------------------------------
	def BumpBottom(self, bumpSprite ):
		pass
	#---------------------------------------------------------------------
	def SetImg(self, newSurface, newRect=None):
		self.image = newSurface
		if newRect:
			self.rect  = newRect
		else:
			self.rect  = newSurface.get_rect()

#-----------------------------------------------------------------------------
class CharactorHUD(SimpleSprite):
	def __init__(self):
		SimpleSprite.__init__( self, 'hud' )
		self.originalImg = self.image.convert_alpha()
		self.charactor = None

	def SetCharactor(self, charactor):
		self.charactor = charactor

	def UpdateAll( self ):
		if not self.charactor:
			log.debug( "hud health changed, but no charactor" )
			return


		log.debug( "redrawing hud" )
		self.image.fill( (0,0,0,0) )

		health = self.charactor.health
		red = (255,0,0)
		for i in range(0,health):
			pos = 18 + i*28
			pygame.draw.circle( self.image, red, (pos, 44), 10)

		shadow = pygame.Surface( (1,16) )
		shadow.fill( (0,0,0) )
		coinRect = pygame.Rect( (6,62,2,16) )

		coins = self.charactor.coins
		try:
			for i in range(len(coins)):
				coinRect.x += 3
				col = coins[i].color
				pygame.draw.rect( self.image, col, coinRect, 0 )
				shadowPos = (coinRect.right, coinRect.y)
				self.image.blit( shadow, shadowPos )
		except Exception, e:
			log.debug( "caught"+ str(e) )
			raise e

		self.image.blit( self.originalImg, (0,0) )
		


#classes for our game objects

#-----------------------------------------------------------------------------
class PowerUp:
	#----------------------------------------------------------------------
	def SetLevel(self, level):
		self.level = level
	#----------------------------------------------------------------------
	def Resurrect(self):
		#don't resurrect
		return 0
	#----------------------------------------------------------------------
	def Die(self):
		self.active = 0
		self.level.SpriteDeath(self)

	#----------------------------------------------------------------------
	def CheckForGlarf( self, bumpSprite ):
		#TODO: this import is ugly
		from charactor_glarf import Charactor
		if isinstance( bumpSprite, Charactor ):
			bumpSprite.addItem( self )
			self.Die()
	#----------------------------------------------------------------------
	def BumpBottom(self, bumpSprite):
		self.CheckForGlarf(bumpSprite)
	#----------------------------------------------------------------------
	def BumpLeft(self, bumpSprite):
		self.CheckForGlarf(bumpSprite)
	#----------------------------------------------------------------------
	def BumpRight(self, bumpSprite):
		self.CheckForGlarf(bumpSprite)
	#----------------------------------------------------------------------
	def BumpTop(self, bumpSprite):
		self.CheckForGlarf(bumpSprite)


#-----------------------------------------------------------------------------
class Superstar(PowerUp, SimpleSprite):
	def __init__(self, level, origin=(100,100)):
		SimpleSprite.__init__(self, 'superstar1')

		import random
		from weapons import DefaultWeapon, FireWeapon, WaterGun
		self.weapon = random.choice( [DefaultWeapon,
		                              FireWeapon,
		                              WaterGun,
		                            ] )

		imgFrame1 = data.pngs[self.weapon.graphicPrefix +'1']
		imgFrame2 = data.pngs[self.weapon.graphicPrefix +'2']
		imgFrame3 = data.pngs[self.weapon.graphicPrefix +'3']

		self.frames = [imgFrame1, imgFrame2, imgFrame3]
		self.frameCounter = 0
		self.hackyAnimationDelay = 0

		self.displayRect = self.rect.move( 0,0 )
		self.rect.inflate( -10, -10 )
		self.origin = origin
		self.rect.topleft = self.origin

		self.active = 1

	#----------------------------------------------------------------------
	def update(self, timeChange):
		self.hackyAnimationDelay += 1
		if self.hackyAnimationDelay < 3:
			return
		self.hackyAnimationDelay = 0
		self.frameCounter = (1+self.frameCounter) % len(self.frames)
		self.image = self.frames[self.frameCounter]

	#----------------------------------------------------------------------
	def NotifyDirtyScreen(self, bgMangr):
		if not self.active and bgMangr.SpriteIsVisible( self.rect ):
			self.active = 1
			self.level.SpriteBirth( self )



#-----------------------------------------------------------------------------
class Coin(PowerUp, AnimatedWidget):
	def __init__(self, level, origin=(100,100)):
		self.myAnim = load_animation( 'coin', 'default' )
		AnimatedWidget.__init__(self, self.myAnim )
		self.displayRect = self.rect.move(0,0)

		self.displayRect = self.rect.move( 0,0 )
		self.rect.inflate( -10, -10 )
		self.origin = origin
		self.originalPos = origin
		self.rect.topleft = self.origin
		self.color = (255,200,0)


		self.active = 1

	#----------------------------------------------------------------------
	def update(self, timeChange):
		AnimatedWidget.update( self, timeChange )

	#----------------------------------------------------------------------
	def NotifyDirtyScreen(self, bgMangr):
		if not self.active and bgMangr.SpriteIsVisible( self.rect ):
			self.active = 1
			self.level.SpriteBirth( self )

	#----------------------------------------------------------------------
	def Clone( self ):
		pos = (self.rect.x + 20, self.rect.y+20)
		newOne =  self.__class__( self.level, pos )
		newOne.SetLevel( self.level )
		self.level.SpriteBirth( newOne )
		return newOne




#-----------------------------------------------------------------------------
class Crate(pygame.sprite.Sprite, Fallable, Movable):
	def __init__(self, level, origin=(100,100)):
		pygame.sprite.Sprite.__init__(self) #call Sprite intializer
		self.image = data.pngs.crate
		self.rect = self.image.get_rect()
		self.origin = origin
		self.rect.topleft = self.origin
		self.displayRect = self.rect.move( 0,0 )

		self.active = 0
		self.moveState = [0,0]
		self.speed     = [3,3]
		self.falling = 1
		self.frictionCoeff = 0.5

	#----------------------------------------------------------------------
	def update(self, timeChange):
		if self.falling:
			self.Fall()

		change = map( operator.mul, self.moveState, self.speed )
		#change = map( int, map( math.ceil, change ) )

		if change == [0,0]:
			return

		newPos = self.rect.move( change )

		solids = self.level.solids
		limiter = self.Blocked( newPos, solids )
		if limiter.topSprite is not None:
			self.BumpTop( limiter.topSprite )
			limiter.topSprite.BumpBottom( self )
		if limiter.right is not None:
			self.BumpRight( limiter.rightSprite )
			limiter.rightSprite.BumpLeft( self )
		if limiter.bottomSprite is not None:
			self.BumpBottom( limiter.bottomSprite )
			limiter.bottomSprite.BumpTop( self )
			#apply friction
			ApplyFriction(self)
		if limiter.left is not None:
			self.BumpLeft( limiter.leftSprite )
			limiter.leftSprite.BumpRight( self )

		self.rect = newPos.move( 0,0 )

		self.falling = 1

	#----------------------------------------------------------------------
	def BumpLeft(self, bumpSprite):
		self.moveState[0] = 1
	#----------------------------------------------------------------------
	def BumpRight(self, bumpSprite):
		self.moveState[0] = -1

	#----------------------------------------------------------------------
	def NotifyDirtyScreen(self, bgMangr):
		if not self.active and bgMangr.SpriteIsVisible( self.rect ):
			self.active = 1
			self.level.SpriteBirth( self )

	#----------------------------------------------------------------------
	def NotifyOutOfBounds(self, bounds):
		self.Die()

	#----------------------------------------------------------------------
	def SetLevel(self, level):
		self.level = level

	#----------------------------------------------------------------------
	def Die(self):
		self.active = 0
		self.level.SpriteDeath(self)
	#----------------------------------------------------------------------
	def Resurrect(self):
		self.rect.topleft = self.origin
		return 1

#-----------------------------------------------------------------------------
class BouncingCrate(Crate, Fallable, Bouncable):
	def __init__(self, level, origin=(100,100)):
		Crate.__init__( self, level, origin )
		self.frictionCoeff = 0.2


#-----------------------------------------------------------------------------
class TriggerZone(pygame.sprite.Sprite):
	def __init__(self, level, pos, size):
		pygame.sprite.Sprite.__init__(self)
		self.rect = pygame.Rect( pos[0],pos[1], *size )
		self.displayRect = self.rect.move(0,0)
		self.image = pygame.Surface( self.rect.size, SRCALPHA, 32 )
		self.origin = self.rect.topleft
		self.level = level

		self.image.fill( (0,0,200,20) )
		drawRect = pygame.Rect( 0,0, *self.rect.size )
		pygame.draw.rect( self.image, (190,90,0), drawRect, 10 )
		#topRect = pygame.Rect( 0, 0, s_r.width, 10 )
		#botRect = topRect.move(0,s_r.height-10)
		#leftRect = pygame.Rect( 0,0,10, s_r.height )
		#rightRect = leftRect.move(s_r.width-10,0)
		#vertImg = pygame.Surface( topRect.size, pygame.SRCALPHA, 32 )
		#vertImg.fill( (190,90,0) )
		#self.image.blit( vertImg, topRect )
		#self.image.blit( vertImg, botRect )
		#horzImg = pygame.Surface( leftRect.size, pygame.SRCALPHA, 32 )
		#horzImg.fill( (190,90,0) )
		#self.image.blit( horzImg, leftRect )
		#self.image.blit( horzImg, rightRect )

	#----------------------------------------------------------------------
	def SetLevel(self, level):
		self.level = level

	#---------------------------------------------------------------------
	def NotifyDirtyScreen(self, bgMangr ):
		pass

	#----------------------------------------------------------------------
	def update(self, timeChange):
		pass
		# maybe this should be a sprite for when the leveleditor is
		# doing stuff

	#----------------------------------------------------------------------
	def Entered( self, enteringSprite ):
		pass

	#----------------------------------------------------------------------
	def Clone( self ):
		newRect = self.rect.move(self.rect.x + 20, self.rect.y+20)
		newOne =  self.__class__( self.level, newRect )
		self.level.AddTriggerZone( newOne )
		return newOne





#this calls the 'main' function when this script is executed
if __name__ == '__main__': 
	print 'you are not supposed to run me'
