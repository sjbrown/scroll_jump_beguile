#!/usr/bin/env python
#Import Modules
import os, pygame
from copy import copy
from pygame.locals import *
from pygame.sprite import Group
import data
from log import log
from anim_widget import AnimatedWidget
from mawjumper import MawJumper
from random import Random
from utils import *
from physics import *

from objects import FACINGLEFT, FACINGRIGHT

#check if we have set (Python version < 2.4)
try:
	set()
except:
	from sets import Set as set

# this module's random number generator
rng = Random()

#-----------------------------------------------------------------------------
class BulletEffect: pass
#-----------------------------------------------------------------------------
class Damager(BulletEffect):
	"an effect that a weapon can have.  simply does damage"
	def __init__(self, power):
		self.power = power

	#----------------------------------------------------------------------
	def Hit( self, target, direction ):
		if hasattr( target, "TakeDamage" ):
			target.TakeDamage( self.power )

	#----------------------------------------------------------------------
	def CombineWith( self, sisterEffect ):
		self.power += rng.randint( 0, sisterEffect.power )
		log.info( 'combined to power: ' + str( self.power) )
#-----------------------------------------------------------------------------
class Stunner(BulletEffect):
	"""an effect that a weapon can have.  stops the movement of the target
	temporarily"""
	def __init__(self, power=100):
		self.power = power

	#----------------------------------------------------------------------
	def Hit( self, target, direction ):
		if hasattr( target, "Stun" ):
			target.Stun( self.power )

	#----------------------------------------------------------------------
	def CombineWith( self, sisterEffect ):
		self.power += rng.randint( 0, sisterEffect.power )
		log.info( 'combined to power: ' + str( self.power) )

#-----------------------------------------------------------------------------
class Bullet(pygame.sprite.Sprite, Movable):
	"""a bullet shot by a weapon."""
	lifetime = 10000
	color = [255,0,0]
	blendableAttributes = [ 'bouncyness',
	                             'lifetime',
	                             'isSolid',
	                             'color',
	                             'effects',
	                           ]
	effects = [ Damager( 30 ), Stunner(100) ]

	def __init__(self, bgMangr, level):
		self.ImgRectInit()
		self.level = level
		self.active = 1

		self.solids = self.level.solids
		self.bgMangr = bgMangr

		self.isSolid = 1

		self.moveState = [0,0]
		self.speed     = [10,10]
		self.isBumpingTop = 0
		self.isBumpingRight = 0
		self.isBumpingBottom = 0
		self.isBumpingLeft = 0

		self.leftFacingImg = self.image
		self.rightFacingImg = self.image
		self.displayRect = self.rect.move(0,0)



	#----------------------------------------------------------------------
	def ImgRectInit(self):
		#this is an abstract method.  The subclass should implement it.
		#It should call pygame.sprite.Sprite.__init__()
		#and should create self.image, self.rect, and self.displayRect
		raise NotImplemented

	#---------------------------------------------------------------------
	def NotifyDirtyScreen(self, bgMangr ):
		pass

	#----------------------------------------------------------------------
	def NotifyOutOfBounds(self, bounds):
		if self.level.HasGoneIntoKillzone( self ):
			self.Die()


	#----------------------------------------------------------------------
	def Die(self):
		self.active = 0
		self.level.SpriteDeath(self)

	#----------------------------------------------------------------------
	def Resurrect(self):
		#don't resurrect
		return 0

	#----------------------------------------------------------------------
	def InitMoveState(self, moveState, facing):
		if facing == FACINGLEFT:
			self.moveState[0] = -self.moveState[0]
		self.moveState = vectorSum( self.moveState, moveState )

	#----------------------------------------------------------------------
	def BumpLeft(self, bumpSprite ):
		Movable.BumpLeft(self,bumpSprite)
		self.Hit( bumpSprite, 'left' )
	#----------------------------------------------------------------------
	def BumpRight(self, bumpSprite ):
		Movable.BumpRight(self,bumpSprite)
		self.Hit( bumpSprite, 'right' )
	#----------------------------------------------------------------------
	def BumpTop(self, bumpSprite ):
		Movable.BumpTop(self,bumpSprite)
		self.Hit( bumpSprite, 'top' )
	#----------------------------------------------------------------------
	def BumpBottom(self, bumpSprite ):
		Movable.BumpBottom(self,bumpSprite)
		self.Hit( bumpSprite, 'bottom' )

	#----------------------------------------------------------------------
	def Hit( self, target, direction ):
		for effect in self.effects:
			effect.Hit( target, direction )

	#----------------------------------------------------------------------
	def update(self, timeChange):
		self.Move( self.solids )

		if self.moveState[0] < 0:
			self.facing = FACINGRIGHT
			self.image = self.rightFacingImg
		if self.moveState[0] > 0:
			self.facing = FACINGLEFT
			self.image = self.leftFacingImg

		self.lifetime -= timeChange
		if self.lifetime < 0:
			self.Die()

#-----------------------------------------------------------------------------
class BounceBullet(Bullet, Fallable, Bouncable, AnimatedWidget): 
	color = [255,0,0]
	def __init__( self, bgMangr, level ):
		Bullet.__init__(self, bgMangr, level)
		Fallable.Init( self )
		self.bouncyness = 0.8
		self.moveState = [1,-1]
		self.speed = [10, 9]
		self.frictionCoeff = 0.1

		#the markForDeath attribute is used because sometimes you
		#can't just call Die() because it'll kill some attributes
		#in the middle of the update() function and then something
		#else will try to use those attributes and an exception is
		#raised and it crashes
		self.markForDeath = 0

		self.blendableAttributes += ['bouncyness']

	#----------------------------------------------------------------------
	def ImgRectInit(self):
		self.airAnim = load_animation( 'ball', 'air' )
		self.squishAnim = load_animation( 'ball', 'squish' )
		AnimatedWidget.__init__(self, self.airAnim )
		self.displayRect = self.rect.move(0,0)

	#----------------------------------------------------------------------
	def kill( self ):
		# we override kill to avoid multiple calls (via inheritance)
		AnimatedWidget.kill( self )

	#----------------------------------------------------------------------
	def Hit( self, target, direction ):
		for effect in self.effects:
			effect.Hit( target, direction )
		if isinstance( target, MawJumper ):
			self.markForDeath = 1
		

	#----------------------------------------------------------------------
	def BumpTop(self, bumpSprite ):
		Bouncable.BumpTop(self,bumpSprite)
		self.SetAnimation( self.squishAnim )
		self.Hit( bumpSprite, 'top' )

	#----------------------------------------------------------------------
	def BumpBottom(self, bumpSprite ):
		ApplyFriction( self )
		Bouncable.BumpBottom(self,bumpSprite)
		self.SetAnimation( self.squishAnim )
		self.Hit( bumpSprite, 'bottom' )

	#----------------------------------------------------------------------
	def BumpLeft(self, bumpSprite ):
		Bouncable.BumpLeft(self,bumpSprite)
		self.Hit( bumpSprite, 'left' )
	#----------------------------------------------------------------------
	def BumpRight(self, bumpSprite ):
		Bouncable.BumpRight(self,bumpSprite)
		self.Hit( bumpSprite, 'right' )

	#----------------------------------------------------------------------
	def update(self, timeChange):
		if self.falling:
			self.Fall()

		Bullet.update( self, timeChange )

		#if we're going really slow, just die.
		if self.speed[0] + self.speed[1] < 1:
			self.markForDeath = 1

		if self.markForDeath:
			self.Die()

		#Bullet.update() can possibly cause this sprite to die.
		#so don't continue with the animation if that's the case
		if not self.active:
			return

		self.falling = 1

		AnimatedWidget.update( self, timeChange )
		self.rightFacingImg = pygame.transform.flip( self.image, 1, 0)

	#----------------------------------------------------------------------
	def AnimationFinished( self ):
		self.SetAnimation( self.airAnim )

	#----------------------------------------------------------------------
	def Die( self ):
		self.level.effects.PlayEffect( 'flash', 
		                               self.rect.center )
		Bullet.Die(self)

#-----------------------------------------------------------------------------
class FloatingFire(Bullet): 
	lifetime = 200
	color = [220,120,0]
	def __init__( self, bgMangr, level ):
		Bullet.__init__(self, bgMangr, level)

		self.leftFacingImg = self.image
		self.rightFacingImg = self.image

		self.moveState = [1,-0.9]

	#----------------------------------------------------------------------
	def ImgRectInit(self):
		pygame.sprite.Sprite.__init__(self)
		self.image = data.pngs['firebullet']
		#self.image = pygame.Surface( (40,40) )
		#self.image.fill( (200,100,0) )
		self.rect = self.image.get_rect()
		self.displayRect = self.rect.move(0,0)

	#----------------------------------------------------------------------
	def InitMoveState(self, moveState, facing):
		if facing == FACINGRIGHT:
			self.moveState[0] = -self.moveState[0]
		self.moveState = vectorSum( self.moveState, moveState )

#-----------------------------------------------------------------------------
class DyingFire(FloatingFire, Fallable): 
	#----------------------------------------------------------------------
	def __init__( self, bgMangr, level ):
		FloatingFire.__init__(self, bgMangr, level)
		Fallable.Init(self)
		self.moveState = [1,-0.5]

	#----------------------------------------------------------------------
	def update(self, timeChange):
		if self.falling:
			self.Fall()

		FloatingFire.update( self, timeChange )

		self.falling = 1

#-----------------------------------------------------------------------------
class Smoke(Bullet): 
	lifetime = 300
	color = [120,120,120]
	def __init__( self, bgMangr, level ):
		Bullet.__init__(self, bgMangr, level)

		self.isSolid = 0

		self.leftFacingImg = self.image
		self.rightFacingImg = self.image

		self.moveState = [rng.uniform(-0.5,0.5),-1.2]

	#----------------------------------------------------------------------
	def ImgRectInit(self):
		pygame.sprite.Sprite.__init__(self)
		self.image = data.pngs['smokebullet']
		#self.image = pygame.Surface( (40,40) )
		#self.image.fill( (100,100,100) )
		self.rect = self.image.get_rect()
		self.displayRect = self.rect.move(0,0)

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
	#----------------------------------------------------------------------
	def InitMoveState(self, moveState, facing):
		pass
		

#-----------------------------------------------------------------------------
class WaterBullet(Bullet, Liquid): 
	lifetime = 1900
	color = [0,0,255]
	def __init__( self, bgMangr, level ):
		Bullet.__init__(self, bgMangr, level)
		Liquid.Init( self )
		self.isSolid = 0

		self.leftFacingImg = self.image
		self.rightFacingImg = self.image

		self.moveState = [1,-1]
		self.speed     = [5,8]

	#----------------------------------------------------------------------
	def ImgRectInit(self):
		pygame.sprite.Sprite.__init__(self)
		self.image = data.pngs['waterbullet']
		#self.image = pygame.Surface( (40,20) )
		#self.image.fill( (0,100,200) )
		self.rect = self.image.get_rect()
		self.displayRect = self.rect.move(0,0)

	#----------------------------------------------------------------------
	def InitMoveState(self, moveState, facing):
		if facing == FACINGLEFT:
			self.moveState[0] = -self.moveState[0]
		self.moveState = vectorSum( self.moveState, moveState )

	#----------------------------------------------------------------------
	def update(self, timeChange):
		if self.falling:
			self.Fall()

		Bullet.update( self, timeChange )

		self.falling = 1

	#----------------------------------------------------------------------
	def BumpLeft(self, bumpSprite ):
		Liquid.BumpLeft(self,bumpSprite)
	#----------------------------------------------------------------------
	def BumpRight(self, bumpSprite ):
		Liquid.BumpRight(self,bumpSprite)
	#----------------------------------------------------------------------
	def BumpTop(self, bumpSprite ):
		Liquid.BumpTop(self,bumpSprite)
	#----------------------------------------------------------------------
	def BumpBottom(self, bumpSprite ):
		Liquid.BumpBottom(self,bumpSprite)


		

#-----------------------------------------------------------------------------
class DefaultWeapon:
	"""a weapon that can be owned by a charactor.  shoots bullets."""
	graphicPrefix = 'superstar_red'
	
	def __init__( self, owner ):
		self.owner = owner

		self.bulletClassList = [ BounceBullet ]
		self.bulletClassListIndex = 0

		self.lastBullet = None
		self.nextBullet = self.GenerateBullet()

		self.rechargeTime = 0
		self.rechargeDelay = 1000

		self.shotOrigin = [10,-50]

		self.blendableAttributes = [ 'rechargeDelay',
		                             'bulletClassList',
		                           ]

	#----------------------------------------------------------------------
	def GetColor( self ):
		#TODO: refine this
		return self.bulletClassList[self.bulletClassListIndex].color

	#----------------------------------------------------------------------
	def RechargeReset( self ):
		self.rechargeTime = self.rechargeDelay

	#----------------------------------------------------------------------
	def update( self, timeChange ):
		self.rechargeTime -= timeChange
		if self.rechargeTime < 1:
			self.rechargeTime = 0

	#----------------------------------------------------------------------
	def GenerateBullet( self ):
		bullet = self.bulletClassList[self.bulletClassListIndex](
		                        self.owner.bgMangr,
		                        self.owner.level )
		self.bulletClassListIndex += 1
		self.bulletClassListIndex %= len(self.bulletClassList)

		return bullet

	#----------------------------------------------------------------------
	def Fire( self ):
		if self.rechargeTime > 1:
			return

		self.RechargeReset()

		if self.owner.facing == FACINGLEFT:
			xOffset = self.shotOrigin[0]
		else:
			xOffset = -self.shotOrigin[0]
		center = ( self.owner.rect.centerx + xOffset,
		           self.owner.rect.centery + self.shotOrigin[1] )
		moveState = copy( self.owner.moveState )

		currentBullet = self.nextBullet

		currentBullet.rect.center = center
		currentBullet.InitMoveState( moveState, self.owner.facing )

		isSolid = currentBullet.isSolid
		self.owner.level.SpriteAdd( currentBullet, isSolid )

		self.lastBullet = currentBullet
		self.nextBullet = self.GenerateBullet()

#-----------------------------------------------------------------------------
class FireWeapon(DefaultWeapon):
	"""a weapon that can be owned by a charactor.  shoots bullets."""

	#for making the powerup image
	graphicPrefix = 'superstar'

	def __init__( self, owner ):
		DefaultWeapon.__init__(self, owner)

		self.bulletClassList = [ DyingFire, FloatingFire, Smoke ]

		self.shotOrigin = [70,-8]

		self.rechargeDelay = 100

#-----------------------------------------------------------------------------
class WaterGun(DefaultWeapon):
	"""a weapon that can be owned by a charactor.  shoots bullets."""
	graphicPrefix = 'superstar_green'

	def __init__( self, owner ):
		DefaultWeapon.__init__(self, owner)

		self.bulletClassList = [ WaterBullet ]

		self.shotOrigin = [10,-50]

		self.rechargeDelay = 200


#-----------------------------------------------------------------------------
class BlendedWeapon(DefaultWeapon):
	def __init__(self, owner, weapon1, weapon2Class):
		self.__class__.__bases__ += ( weapon2Class, )
		weapon2Class.__init__(self,owner)


		b1 = weapon1.blendableAttributes 
		b2 = self.blendableAttributes 
		# [ 'bouncyness',
		#   'lifetime',
		#   'isSolid',
		#   'color',
		#   'effects',
		# ]
		for att in b1:
			if (att in b2) and (hasattr( self, 'Blend_'+att )):
				method = getattr(self, 'Blend_'+att )
				method(weapon1)

	def Blend_rechargeDelay( self, weapon1 ):
		minDelay = min( weapon1.rechargeDelay, self.rechargeDelay )
		maxDelay = max( weapon1.rechargeDelay, self.rechargeDelay )
		self.rechargeDelay = rng.randint( minDelay, maxDelay )
		log.info( 'set rechargeDelay to '+ str(self.rechargeDelay) )

	def Blend_bulletClassList( self, weapon1 ):
		#TODO: multiple weapons
		newClass = BulletBlendingClassFactory().Blend( 
		                self.bulletClassList[0],
		                weapon1.bulletClassList[0]
		                )
		self.bulletClassList = [ newClass ]
		self.nextBullet = self.GenerateBullet()
		log.info( 'set bulletClassList to '+ str(self.bulletClassList) )



#-----------------------------------------------------------------------------
class BulletBlendingClassFactory:
	"""A BulletBlendingClassFactory takes as input to its Blend() method
	two *classes* (not instances) to be blended together.  The remaining
	methods are helper functions to Blend() that dictate how to blend
	particular Bullet attributes"""
	def Blend( self, bClass1, bClass2 ):
		#create our new class, start it out the same as bClass1
		#NOTE: it's important to use inheritance here instead of
		#      assignment, otherwise when you change the methods in 
		#      the newClass, you'd change them in the original
		class newClass( bClass1 ): pass

		attList1 = bClass1.blendableAttributes
		attList2 = bClass2.blendableAttributes
		#get the attributes that are in both:
		attList = set( attList1 ).intersection( attList2 )
		for att in attList:
			try:
				myMethod = getattr(self, 'Blend_'+att )
				myMethod(newClass, bClass2)
			except:
				pass

		return newClass

	def Blend_lifetime(self, newClass, bClass2):
		if newClass.lifetime > bClass2.lifetime:
			return
		newClass.lifetime = rng.randint( newClass.lifetime, 
		                                 bClass2.lifetime )
		log.info( 'set lifetime to '+ str(newClass.lifetime) )

	def Blend_effects(self, newClass, bClass2):
		unmatchedList1 = copy( newClass.effects )
		unmatchedList2 = copy( bClass2.effects )

		#Section 1: combine any duplicate effects
		for ef1 in newClass.effects:
			for ef2 in bClass2.effects:
				if ef1.__class__ == ef2.__class__:
					newEf = copy( ef1 )
					unmatchedList2.remove( ef2 )
					unmatchedList1.remove( ef1 )
					newEf.CombineWith(ef2)

		#Section 2: randomly mix any unmatched effects
		for ef1 in unmatchedList1:
			newClass.effects.remove( ef1 )
		#combine them all into one list
		mixedList = unmatchedList1 + unmatchedList2
		if mixedList:
			#shuffle that list
			rng.shuffle( mixedList )
			#take only some (halfish) of the mixed bag of effects
			for i in range( 0, len( mixedList )/2 +1 ):
				newClass.effects.append( copy(mixedList[i]) )




#this calls the 'main' function when this script is executed
if __name__ == '__main__': 
	print 'you are not supposed to run me'
