import os, pygame, operator, math
from copy import copy
from pygame.locals import *
from log import log

from physics import Fallable, Movable, GRAVITY

from scrollGroup import ScrollSpriteGroup, IdlerSpriteGroup
from utils import *
import data

RIGHT = 0
LEFT  = 1

#-----------------------------------------------------------------------------
class MawJumper(pygame.sprite.Sprite, Fallable, Movable):
	def __init__(self, level, origin=(100,100)):
		pygame.sprite.Sprite.__init__(self) #call Sprite intializer
		self.image = data.pngs.chimp
		self.rect = self.image.get_rect()
		self.leftFacingImg = self.image
		self.rightFacingImg = pygame.transform.flip( self.image, 1, 0)
		self.origin = origin
		self.rect.topleft = self.origin
		self.displayRect = self.rect.move( 0,0 )

		self.facing = LEFT

		self.active = 0
		self.moveState = [0,1]
		self.speed     = [6,6]
		self.dizzy = 0
		self.stunTimeout = 0
		self.dying = 0
		self.health = 100
		self.level = level

		self.falling = 1
		self.jumping = 0
		self.landing = 0
		self.peaking = 0
		self.walking = 0

		self.isBumpingTop = 0
		self.isBumpingRight = 0
		self.isBumpingBottom = 0
		self.isBumpingLeft = 0
		self.bumpingForgivenessTimeout = 200

		self.brain = SeekingArtificialIntelligence( self )
		self.SetVelocityRight()

		self.snd_htop = data.oggs['top']

	#----------------------------------------------------------------------
	def NotifyDirtyScreen(self, bgMangr):
		if not self.active and bgMangr.SpriteIsVisible( self.rect ):
			newlyExposedRects = bgMangr.newlyExposedArea
			if newlyExposedRects[0].collidepoint(self.rect.center) \
		   	 or newlyExposedRects[1].collidepoint(self.rect.center):
				#print "monkey sprite birth!"
				self.active = 1
				self.level.SpriteBirth( self )

	#----------------------------------------------------------------------
	def NotifyOutOfBounds(self, bounds):
		if not self.dying:
			log.debug( "MawJumper WENT OFF THE MAP" )
			self.Die()

	#----------------------------------------------------------------------
	def SetLevel(self, level):
		self.level = level

	#----------------------------------------------------------------------
	def StopHorizontal( self ):
		self.walking = 0
		self.moveState[0] = 0

	#----------------------------------------------------------------------
	def TurnAround( self ):
		log.debug( 'turning around -- '+ str(self.facing) )
		self.walking = 1
		if self.facing == RIGHT:
			self.facing = LEFT
			self.image = self.leftFacingImg
			Movable.SetVelocityLeft( self )
		else:
			self.facing = RIGHT
			self.image = self.rightFacingImg
			Movable.SetVelocityRight( self )

	#----------------------------------------------------------------------
	def Jump( self ):
		if self.jumping:
			return
		if self.falling and not ( self.isBumpingBottom or \
		                          self.isBumpingLeft or \
					  self.isBumpingRight ):
			return
		JUMP_POWER = 2.1
		self.jumping = 1
		self.landing = 0
		self.peaking = 0
		self.falling = 0
		if self.facing == RIGHT:
			self.moveState[0] = -1
		else:
			self.moveState[0] = 1
		self.moveState[1] = self.moveState[1] -JUMP_POWER
		Event( 'MawJumperJumps', self, self.rect.center )

	#----------------------------------------------------------------------
	def ContinueJumping( self ):
		mState = self.moveState
		oldUpwardVelocity = mState[1]
		mState[1] = mState[1] + GRAVITY
		if mState[1] >= 0:
			self.jumping = 0
			self.startedFalling = 1
			self.falling = 1
			self.peaking = 0
		#if we're still jumping, but almost at 0, we're peaking
		#calculate this by "if we only went up 10% of our height or less
		elif abs(mState[1]*self.speed[1]) < self.rect.height/10.0:
			self.peaking =1

	#----------------------------------------------------------------------
	def StopJump( self ):
		if self.jumping:
			self.moveState[1] = 0
			self.jumping = 0
			self.startedFalling = 1
			self.falling = 1

	#----------------------------------------------------------------------
	def BumpLeft(self, bumpSprite ):
		self.isBumpingLeft = 1
		Movable.BumpLeft( self, bumpSprite )
	#----------------------------------------------------------------------
	def BumpRight(self, bumpSprite ):
		self.isBumpingRight = 1
		Movable.BumpRight( self, bumpSprite )
	#----------------------------------------------------------------------
	def BumpBottom( self, bumpSprite ):
		self.jumping = 0
		self.moveState[0] = 0
		self.isBumpingBottom = 1
		self.bumpingForgivenessTimeout = 200
		Movable.BumpBottom( self, bumpSprite )

	#----------------------------------------------------------------------
	def update(self, timeChange):
		"walk or spin, depending on the monkeys state"
		if self.dizzy:
			self._spin()
			return
		elif self.dying:
			self.Dying()
			return

		if self.falling:
			self.Fall()

		if self.jumping:
			choices = [ self.ContinueJumping,
				    self.StopJump,
				  ]
		if self.walking:
			choices = [ self.Jump,
				    self.StopHorizontal,
				  ]
		else:
			choices = [ self.Jump,
			            self.TurnAround,
			          ]

		if self.stunTimeout <= 0:
			choice = self.brain.DecideChoice( choices, timeChange )
			if choice:
				choice()
		else: 
			self.stunTimeout -= timeChange

		self.Move( self.level.solids )

		self.bumpingForgivenessTimeout -= timeChange
		if self.bumpingForgivenessTimeout < 1:
			self.bumpingForgivenessTimeout = 0
			self.isBumpingTop= 0
			self.isBumpingRight = 0
			self.isBumpingBottom = 0
			self.isBumpingLeft = 0

		self.falling = 1


	#----------------------------------------------------------------------
	def Dying(self):
		self.level.SpriteDeath(self)
		self.active = 0
		return
		
		self.dying = self.dying + 12
		if self.dying >= 360:
			self.dying = 0
			self.image = self.rightFacingImg
			self.level.SpriteDeath(self)

	#----------------------------------------------------------------------
	def _spin(self):
		"spin the monkey image"
		center = self.rect.center
		self.dizzy = self.dizzy + 12
		if self.dizzy >= 360 or self.dying:
			self.dizzy = 0
			self.image = self.rightFacingImg
		else:
			rotate = pygame.transform.rotate
			self.image = rotate( self.rightFacingImg, 
			                     self.dizzy )
		self.rect = self.image.get_rect()
		self.rect.center = center

	#----------------------------------------------------------------------
	def Die(self):
		#print 'monkey calls DIE'
		self.level.effects.PlayEffect( 'explosion', 
		                               self.rect.center )
		self.dying  = 1

	#----------------------------------------------------------------------
	def Resurrect(self):
		self.dying  = 0
		self.health = 100
		self.rect.topleft = self.origin
		return 1

	#----------------------------------------------------------------------
	#:def Hit(self, bumpSprite ):
	#----------------------------------------------------------------------
	def BumpTop(self, bumpSprite ):
		damage = 60
		"this will cause the monkey to start spinning"
		if not self.dizzy and not self.dying:
			self.snd_htop.play()
			self.dizzy = 1
			self.TakeDamage( damage, bumpSprite )

	#---------------------------------------------------------------------
	def TakeDamage( self, damage, source=None ):
		self.health = self.health - damage
		if self.health < 0:
			self.health = 0
			self.Die()

	#---------------------------------------------------------------------
	def Stun( self, stunPower=100, source=None ):
		self.stunTimeout = stunPower

	#---------------------------------------------------------------------
	def GetSaveString(self):
		return str( self.origin ) +', ()'


#-----------------------------------------------------------------------------
class SeekingArtificialIntelligence:
	def __init__( self, sprite ):
		self.sprite = sprite
		self.sightDistance = 300
		self.turningTimeout = 1500
		self.walkingTimeout = 3500

	#---------------------------------------------------------------------
	def DecideChoice(self, choices, timeChange):
		"""Returns the choice that it wants to make"""
		s = self.sprite

		nameFnMapping = {}
		for c in choices:
			nameFnMapping[c.__name__] = c

		if s.jumping and 'ContinueJumping' in nameFnMapping.keys():
			return nameFnMapping['ContinueJumping']

		sightRect = s.rect.move( (0,0) )
		sightRect.width += self.sightDistance
		if s.facing == RIGHT:
			sightRect.x -= self.sightDistance

		target = s.level.charactor
		if sightRect.colliderect( target.rect ):
			if 'Jump' in nameFnMapping.keys():
				return nameFnMapping['Jump']

		self.walkingTimeout -= timeChange
		if s.walking and self.walkingTimeout < 1:
			self.walkingTimeout = 500
			if 'StopHorizontal' in nameFnMapping.keys():
				return nameFnMapping['StopHorizontal']
		elif self.walkingTimeout < 1:
			self.walkingTimeout = 3500

		self.turningTimeout -= timeChange
		if self.turningTimeout < 1:
			self.turningTimeout = 1500
			if 'TurnAround' in nameFnMapping.keys():
				return nameFnMapping['TurnAround']

		return None

