
import os, pygame, operator, math
from copy import copy
from pygame.locals import *


GRAVITY = 0.09
FRICTION = 0.6
MAX_FALL = 3


		
#-----------------------------------------------------------------------------
class BoundingBox:
	def __init__(self):
		self.top = None
		self.right = None
		self.bottom = None
		self.left = None

		self.topSprite = None;
		self.rightSprite = None;
		self.bottomSprite = None;
		self.leftSprite = None;

	#---------------------------------------------------------------------
	def SetBottom(self, sprite ):
		self.bottomSprite = sprite

#-----------------------------------------------------------------------------
class Fallable:
	"""interface for things that can fall"""
	def Init( self ):
		self.falling = 0
	#----------------------------------------------------------------------
	def Fall( self ):
		maxFall = MAX_FALL
		fallRate = GRAVITY
		if hasattr( self, 'fallLimit' ):
			maxFall = self.fallLimit
		if hasattr( self, 'featherFall' ):
			fallRate = GRAVITY - self.featherFall

		if self.moveState[1] < maxFall:
			self.moveState[1] = self.moveState[1] + fallRate

#------------------------------------------------------------------------------
class Movable:
	"""interface for things that can move and get bumped"""
	#----------------------------------------------------------------------
	def SetVelocityLeft( self ):
		self.moveState[0] = -1

	#----------------------------------------------------------------------
	def SetVelocityRight( self ):
		self.moveState[0] = 1

	#----------------------------------------------------------------------
	def StopLeft( self ):
		if self.moveState[0] is -1:
			self.moveState[0] = 0
	
	#----------------------------------------------------------------------
	def StopRight( self ):
		if self.moveState[0] is 1:
			self.moveState[0] = 0

	#----------------------------------------------------------------------
	def BumpLeft(self, bumpSprite ):
		pass
	#----------------------------------------------------------------------
	def BumpRight(self, bumpSprite ):
		pass
	#----------------------------------------------------------------------
	def BumpBottom(self, bottomSprite ):
		if self.moveState[1] > 0:
			self.moveState[1] = 0
	#----------------------------------------------------------------------
	def BumpTop(self, topSprite ):
		self.jumping = 0
		self.falling = 1
		if self.moveState[1] < 0:
			self.moveState[1] = 0


	#----------------------------------------------------------------------
	def Blocked( self, newRect, spriteGroup ):
		"""See if self would be blocked by sprites in spriteGroup
		if self were to move to newRect (a Rect)
		Tries to change newRect to accommodate the blockers"""
		limiter = BoundingBox()
		oldPos = self.rect.move( 0,0 )

		self.rect = newRect.move( 0,0 )

		colliders = pygame.sprite.spritecollide( self, spriteGroup, 0)

		self.rect = oldPos


		if len(colliders)  is not 0:
			for sprite in colliders:

				if ( limiter.top is None \
				   or sprite.rect.bottom > limiter.top ) \
				   and newRect.top      < sprite.rect.bottom \
				   and oldPos.top        >= sprite.rect.bottom:
					newRect.top         = sprite.rect.bottom
					limiter.top        = sprite.rect.bottom
					limiter.topSprite  = sprite

				if ( limiter.right is None  \
				   or sprite.rect.left  < limiter.right ) \
				   and newRect.right    > sprite.rect.left \
				   and oldPos.right      <= sprite.rect.left:
					newRect.right         = sprite.rect.left
					limiter.right        = sprite.rect.left
					limiter.rightSprite  = sprite

				if ( limiter.bottom is None \
				   or sprite.rect.top < limiter.bottom ) \
				   and newRect.bottom > sprite.rect.top \
				   and oldPos.bottom   <= sprite.rect.top:
					newRect.bottom        = sprite.rect.top
					limiter.bottom       = sprite.rect.top
					#TODO: why does this work with a setter?
					limiter.SetBottom( sprite )

				if ( limiter.left is None \
				   or sprite.rect.right  > limiter.left ) \
				   and newRect.left   < sprite.rect.right \
				   and oldPos.left     >= sprite.rect.right:
					newRect.left       = sprite.rect.right
					limiter.left       = sprite.rect.right
					limiter.leftSprite = sprite
			

		return limiter

	#----------------------------------------------------------------------
	def Move( self, solids ):
		#the change in position is the direction they're moving 
		#times the speed they're going
		change = map(operator.mul, self.moveState, self.speed )

		#round anything (above 0 but under 1) up to 1
		#this helps us detect if the charactor is standing on something
		# - it forces a proper BumpBottom
		if change[0] > 0 and change[0] < 1:
			change[0] = 1
		if change[1] > 0 and change[1] < 1:
			change[1] = 1


		if change == [0,0]:
			return

		newPos = self.rect.move( change )

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
		if limiter.left is not None:
			self.BumpLeft( limiter.leftSprite )
			limiter.leftSprite.BumpRight( self )

		self.rect = newPos.move( 0,0 )

#------------------------------------------------------------------------------
class Bouncable(Movable):
	#----------------------------------------------------------------------
	def BumpLeft(self, leftSprite ):
		self.moveState[0] = -self.moveState[0]
	#----------------------------------------------------------------------
	def BumpRight(self, rightSprite ):
		self.moveState[0] = -self.moveState[0]

	#----------------------------------------------------------------------
	def BumpBottom(self, bottomSprite ):
		bounce = self.__dict__.get( 'bouncyness', 0.3 )

		#if it was going down, reflect it (times the bouncyness)
		if self.moveState[1] > 0:
			if hasattr( self, 'speed' ):
				self.speed[1] = (self.speed[1]*bounce)
				self.moveState[1] = -self.moveState[1]
			else:
				self.moveState[1] = -(self.moveState[1]*bounce)

	#def Blocked( self, newpos, group ):
		#limiter = Movable.Blocked(self, newpos, group )
		#if limiter.leftSprite: print limiter
		#return limiter

#-----------------------------------------------------------------------------
class Liquid( Movable, Fallable ):
	#----------------------------------------------------------------------
	def __init__(self):
		self.frictionCoeff = 0.01
	#----------------------------------------------------------------------
	def BumpLeft(self, bumpSprite ):
		pass
	#----------------------------------------------------------------------
	def BumpRight(self, bumpSprite ):
		pass
	#----------------------------------------------------------------------
	def BumpBottom(self, bottomSprite ):
		if self.moveState[1] > 0:
			self.moveState[1] = 0
	#----------------------------------------------------------------------
	def BumpTop(self, topSprite ):
		pass

#-----------------------------------------------------------------------------
def ApplyFriction( obj ):
	friction = FRICTION

	if hasattr( obj, 'frictionCoeff' ):
		friction *= obj.frictionCoeff

	if hasattr( obj, 'speed' ):
		obj.speed[0] -= (obj.speed[0] * friction)

	else:
		obj.moveState[0] -= (obj.moveState[0] * friction)



