from anim_widget import AnimatedWidget
from physics import Fallable, Movable
from utils import *
from objects import *
from log import log
import data
import random
from weapons import DefaultWeapon, FireWeapon, WaterGun, BlendedWeapon
#import all the key codes
from pygame.constants import *




#-----------------------------------------------------------------------------
class Charactor(AnimatedWidget, Fallable, Movable):
	"""moves a charactor on the screen, following the mouse"""
	def __init__(self, bgMangr):
		self.walkAnim = load_animation( 'glarf', 'walk' )
		self.restAnim = load_animation( 'glarf', 'rest' )
		self.turnAnim = load_animation( 'glarf', 'turn' )
		self.jumpAnim = load_animation( 'glarf', 'jump' )
		self.peakAnim = load_animation( 'glarf', 'peak' )
		self.fallAnim = load_animation( 'glarf', 'fall' )
		self.landAnim = load_animation( 'glarf', 'land' )
		AnimatedWidget.__init__(self, self.restAnim)
		self.bgMangr = bgMangr
		self.level = None
		self.weapon = None
		self.firing = 0
		self.active = 1
		self.walking = 0
		self.duckingTimer = None
		self.lookingAround = 0
		self.turning = 0

		self.facing = FACINGLEFT
		self.leftFacingImg = self.image
		self.rightFacingImg = pygame.transform.flip( self.image, 1, 0)

		self.rect.midbottom = ( 200, 200 )
		self.displayRect = self.rect.move(0,0)
		#self.area = screen.get_rect().inflate(50,50)
		#self.oldPos = self.rect

		self.InitControls()

		self.moveState = [0,0]
		self.speed     = [10,10]
		self.jumping = 0
		self.peaking = 0
		self.startedFalling = 0
		self.landing = 0
		self.ducking = 0
		self.isOnSomeGround = 0
		Fallable.Init( self )
		self.isBumpingTop = 0
		self.isBumpingRight = 0
		self.isBumpingBottom = 0
		self.isBumpingLeft = 0
		self.bumpingForgivenessTimeout = 200

		self.falling = 0
		self.health  = 3
		self.invulnerable = 0
		self.invulnerableTimeout = 1000

		self.coins = []

		self.snd_jump = data.oggs.jump
		self.snd_land = data.oggs.land


	#----------------------------------------------------------------------
	def SetLevel(self, level):
		self.level = level
		weaponClass = DefaultWeapon
		if hasattr( self.level, "defaultWeaponClass" ):
			weaponClass = self.level.defaultWeaponClass
		self.weapon = weaponClass( self )

	#----------------------------------------------------------------------
	def InitControls(self):
		uprof = data.userProfile
		self.listenKeys = { 
		      stringToKey( uprof['up'] ): self.MoveUp,
		      stringToKey( uprof['down'] ): self.MoveDown,
		      stringToKey( uprof['left'] ): self.SetVelocityLeft,
		      stringToKey( uprof['right'] ): self.SetVelocityRight,
		      stringToKey( uprof['jump'] ): self.MoveUp,
		      stringToKey( uprof['fire'] ): self.Fire,
		  }

		self.offKeys = {
		      stringToKey( uprof['up'] ): self.StopJump,
		      stringToKey( uprof['down'] ): self.StopDown,
		      stringToKey( uprof['left'] ): self.StopLeft,
		      stringToKey( uprof['right'] ): self.StopRight,
		      stringToKey( uprof['jump'] ): self.StopJump,
		      stringToKey( uprof['fire'] ): self.StopFire,
		  }


	#----------------------------------------------------------------------
	def NotifyDirtyScreen(self, bgMangr):
		pass
	#----------------------------------------------------------------------
	def NotifyOutOfBounds(self, bounds):
		if self.level.HasGoneIntoKillzone( self ):
			log.debug("GLARF WENT OFF THE MAP")
			#print self.rect, bounds
			#TODO: this is a bug here.  what if glarf is looking
			# around while falling?
			if self.active and not self.lookingAround: 
				self.Die()

	#----------------------------------------------------------------------
	def update(self, timeChange):
		#make it so the charactor is always dirty.  
		#the player-controlled guy is always animating.
		self.dirty = 1

		self.DecideAnimation()
		self.isOnSomeGround = 0

		if self.invulnerable:
			self.invulnerableTimeout -= timeChange
			if self.invulnerableTimeout < 1:
				self.invulnerable = 0
		if self.jumping:
			self.ContinueJumping()
		elif self.falling:
			self.Fall()

		if self.ducking:
			self.duckingTimer += timeChange
			if self.duckingTimer > 1000:
				self.StartLookingAround()


		self.weapon.update( timeChange )
		if self.firing:
			self.weapon.Fire()

		self.bumpingForgivenessTimeout -= timeChange
		if self.bumpingForgivenessTimeout < 1:
			self.bumpingForgivenessTimeout = 0
			self.isBumpingTop= 0
			self.isBumpingRight = 0
			self.isBumpingBottom = 0
			self.isBumpingLeft = 0

		self.Move( self.level.solids )

		if not self.active:
			#earlier in this update function, active was set to 
			#false (ie, the charactor was killed) so don't bother
			#with the graphics; just return
			return

		AnimatedWidget.update( self, timeChange )
		self.rightFacingImg = pygame.transform.flip( self.image, 1, 0)

		if self.moveState[0] < 0:
			#print 'ms - setting facing left'
			self.facing = FACINGLEFT
			self.image = self.leftFacingImg
		if self.moveState[0] > 0:
			#print 'ms - setting facing right'
			self.facing = FACINGRIGHT
			self.image = self.rightFacingImg
		else:
			if self.facing == FACINGRIGHT:
				self.image = self.rightFacingImg
			elif self.facing == FACINGLEFT:
				self.image = self.leftFacingImg

		if self.lookingAround:
			howFarDown = min( 400, (self.duckingTimer-1000)/7)
			lookRect = self.rect.move( (0,howFarDown) )
			self.bgMangr.NotifyPlayerSpritePos(lookRect)
		else:
			self.bgMangr.NotifyPlayerSpritePos(self.rect)

		#not necessarily true, but makes things convenient to think
		# of a physical body as "always falling"
		self.falling = 1



	#----------------------------------------------------------------------
	def DecideAnimation(self):
		if self.turning != 0 and self.animation != self.turnAnim:
			log.debug('setting turn')
			self.turnAnim.Reset()
			self.SetAnimation( self.turnAnim )
		elif self.jumping and self.animation != self.jumpAnim \
		  and not self.peaking \
		  and not self.turning:
			log.debug( 'setting jump' )
			self.jumpAnim.Reset()
			self.SetAnimation( self.jumpAnim )
		elif self.jumping and self.peaking \
		  and self.animation != self.peakAnim \
		  and not self.turning:
			log.debug( 'setting peak' )
			self.peakAnim.Reset()
			self.SetAnimation( self.peakAnim )
		elif self.landing and self.animation == self.fallAnim \
		  and not self.turning:
			log.debug( 'setting land' )
			self.landAnim.Reset()
			self.SetAnimation( self.landAnim )
			#mark here
			#self.landing = 0
		elif self.startedFalling and self.animation != self.fallAnim \
		  and not self.turning:
			log.debug( 'setting fall' )
			self.fallAnim.Reset()
			self.SetAnimation( self.fallAnim )
			self.startedFalling = 0
		elif self.walking and self.animation != self.walkAnim \
		  and self.isOnSomeGround \
		  and not (self.turning or self.jumping or self.startedFalling):
			log.debug( 'setting walk' )
			self.SetAnimation( self.walkAnim )
		elif self.animation != self.restAnim \
		  and self.isOnSomeGround \
		  and not (self.turning or self.jumping or self.startedFalling \
		           or self.walking or self.landing):
			log.debug( 'setting rest' )
			self.SetAnimation( self.restAnim )


	#----------------------------------------------------------------------
	def AnimationFinished(self ):
		self.walkAnim.Reset()
		if self.animation == self.turnAnim:
			self.turning = 0
		if self.animation == self.jumpAnim:
			#can't reset jump here, that'll make it loop
			return
		if self.animation == self.fallAnim:
			#can't reset fall here, that'll make it loop
			return
		if self.animation == self.landAnim:
			#can't reset land here, that'll make it loop
			self.landing = 0
		if self.animation == self.walkAnim:
			log.debug( 'setting walk' )
			self.SetAnimation( self.walkAnim )

	#----------------------------------------------------------------------
	def BumpTop(self, topSprite ):
		if not self.active:
			#self died in this current update so don't do anything
			return
		Movable.BumpTop( self, topSprite )

	#----------------------------------------------------------------------
	def BumpRight(self, bumpSprite ):
		if not self.active:
			#self died in this current update so don't do anything
			return
		self.isBumpingRight = 1
		self.bumpingForgivenessTimeout = 200
		enemyGroup = self.level.enemyGroup
		if bumpSprite in enemyGroup.sprites():
			self.EnemyBump( bumpSprite )


	#----------------------------------------------------------------------
	def BumpBottom(self, bottomSprite ):
		if not self.active:
			#self died in this current update so don't do anything
			return
		self.isBumpingBottom = 1
		self.bumpingForgivenessTimeout = 200
		if self.moveState[1] > 0:
			self.isOnSomeGround = 1
		if self.moveState[1] > 0 and self.animation == self.fallAnim:
			self.landing = 1
			print 'setting landing'
			print 'bottom sprit is', bottomSprite
		if self.moveState[1] > 2:
			self.snd_land.play()
		self.moveState[1] = 0

	#----------------------------------------------------------------------
	def BumpLeft(self, bumpSprite ):
		if not self.active:
			#self died in this current update so don't do anything
			return
		self.isBumpingLeft = 1
		self.bumpingForgivenessTimeout = 200
		enemyGroup = self.level.enemyGroup
		if bumpSprite in enemyGroup.sprites():
			self.EnemyBump( bumpSprite )


	#----------------------------------------------------------------------
	def EnemyBump(self, bumpSprite ):
		if self.invulnerable:
			return
		self.health -= 1
		Event( 'GlarfHurt', self, self.rect.center )

		self.invulnerable = 1
		self.invulnerableTimeout = 1000

		if self.active and self.health == 0:
			self.level.effects.PlayEffect( 'explosion', 
			                               self.rect.center )
			self.Die()
	
	#----------------------------------------------------------------------
	def SetVelocityLeft( self ):
		log.debug( 'set vel left -- '+ str(self.facing) )
		if self.facing == FACINGRIGHT:
			self.turning = 'left'
		self.walking = 1
		Movable.SetVelocityLeft( self )
	#----------------------------------------------------------------------
	def SetVelocityRight( self ):
		log.debug( 'set vel right -- '+ str(self.facing) )
		if self.facing == FACINGLEFT:
			self.turning = 'right'
		self.walking = 1
		Movable.SetVelocityRight( self )
	#----------------------------------------------------------------------
	def StopLeft( self ):
		self.walking = 0
		Movable.StopLeft( self )
	#----------------------------------------------------------------------
	def StopRight( self ):
		print "stopping right"
		self.walking = 0
		Movable.StopRight( self )
	#----------------------------------------------------------------------
	def MoveUp( self ):
		self.Jump()

	#----------------------------------------------------------------------
	def Jump( self ):
		if self.jumping:
			return
		if self.falling and not ( self.isBumpingBottom or \
		                          self.isBumpingLeft or \
					  self.isBumpingRight ):
			return
		JUMP_POWER = 2.1
		self.snd_jump.play()
		self.jumping = 1
		self.landing = 0
		self.peaking = 0
		self.falling = 0
		self.moveState[1] = self.moveState[1] -JUMP_POWER

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
	def Fire( self ):
		if not self.firing:
			self.firing = 1

	#----------------------------------------------------------------------
	def StopFire( self ):
		self.firing = 0
	

	#----------------------------------------------------------------------
	def MoveDown( self ):
		if not self.jumping:
			self.ducking = 1
			self.duckingTimer = 0

	#----------------------------------------------------------------------
	def StopDown( self ):
		self.duckingTimer = None
		self.ducking = 0
		if self.moveState[1] is 1:
			self.moveState[1] = 0
		if self.lookingAround:
			self.StopLookingAround()

	#----------------------------------------------------------------------
	def StartLookingAround(self):
		self.lookingAround = 1
		#TODO: this should send out some kind of 'pause' signal, maybe
	#----------------------------------------------------------------------
	def StopLookingAround(self):
		self.lookingAround = 0

	#----------------------------------------------------------------------
	def Die(self):
		Event( 'GlarfDeath', self, self.rect.center )
		self.moveState[0] = 0
		self.active = 0
		self.level.SpriteDeath(self)
	
	#----------------------------------------------------------------------
	def SignalKey( self, event ):
		if not self.active:
			return

		if self.listenKeys.has_key( event.key ) \
		  and event.type is KEYDOWN:
			self.listenKeys[event.key]( )
		elif self.offKeys.has_key( event.key ) \
		  and event.type is KEYUP:
			self.offKeys[event.key]( )

	#----------------------------------------------------------------------
	def addItem(self, item):
		if isinstance( item, Superstar ):
			#randomly choose a weapon class
			weaponClass = item.weapon
			if random.Random().choice( [True, False] ):
				self.weapon = BlendedWeapon( self, self.weapon, weaponClass)
			else:
				self.weapon = weaponClass(self)
			Event( 'PowerupConsume', item, item.rect.center )
		elif isinstance( item, Coin ):
			self.coins.append( item )
			Event( 'CoinConsume', item, item.rect.center )

