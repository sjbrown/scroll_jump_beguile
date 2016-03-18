import pygame
import data
import os



#------------------------------------------------------------------------------
class Explosion(pygame.sprite.Sprite):
	#TODO: this still doesn't fade the stuff out gradually!!
	def __init__(self, position):
		pygame.sprite.Sprite.__init__(self) #call Sprite initializer

    		fullname = os.path.join('data', 'explode_text.png')
        	image = pygame.image.load(fullname)
		rect = image.get_rect()
		self.image_1, self.rect_1 = image, rect

    		fullname = os.path.join('data', 'explode_star1.png')
        	image = pygame.image.load(fullname)
		rect = image.get_rect()
		self.image_2, self.rect_2 = image, rect

    		fullname = os.path.join('data', 'explode_star2.png')
        	image = pygame.image.load(fullname)
		rect = image.get_rect()
		self.image_3, self.rect_3 = image, rect

		self.rect = self.rect_1.unionall( (self.rect_1,
		                                  self.rect_2,
		                                  self.rect_3) ).inflate(30,30)
		self.rect.topleft = [0,0]
		self.rect_1.centerx = self.rect.centerx
		self.rect_1.bottom = self.rect.bottom
		self.rect_2.center = self.rect.center
		self.rect_3.center = self.rect.center
		self.rect.center = position
		self.displayRect = self.rect.move(0,0)

		self.image = pygame.Surface( self.rect.size )
		self.counter = 0
	#---------------------------------------------------------------------
	def NotifyDirtyScreen(self, bgMangr ):
		pass
	#----------------------------------------------------------------------
	def update(self):
		self.counter += 4

		if self.counter >= 254:
			self.kill()
			return

		#--------1
		self.rect_1.move_ip( 0, -1 )
		#img = self.image_1.convert()
		#img.set_colorkey( img.get_at( [0,0] ) )
		#img.set_alpha( 255 - (self.counter +2) )
		#img = img.convert_alpha()
		self.image_1.set_alpha( 255 - (self.counter +2) )
		#self.image_1.alpha -= 0.09

		#--------2
		self.rect_2.move_ip( -1, 0 )
		#img2= self.image_2.convert()
		#img2.set_colorkey( img2.get_at( [0,0] ) )
		#img2 = img2.convert_alpha()
		self.image_2.set_alpha( 255 - self.counter )

		#--------2
		self.rect_3.move_ip( 1, 0 )
		#img3= self.image_3.convert()
		#img3= self.image_3.convert()
		#img3.set_colorkey( img3.get_at( [0,0] ) )
		#img3.set_alpha( 15 + self.counter )
		#img3 = img3.convert_alpha()
		self.image_3.set_alpha( 15 + self.counter )

		self.image = pygame.Surface( self.rect.size ).convert_alpha()
		self.image.fill( [0,0,0,0] )
		self.image.blit( self.image_2, self.rect_2.topleft )
		self.image.blit( self.image_3, self.rect_3.topleft )
		self.image.blit( self.image_1, self.rect_1.topleft )

#------------------------------------------------------------------------------
class FlashEffect(pygame.sprite.Sprite):
	def __init__(self, position):
		pygame.sprite.Sprite.__init__(self) #call Sprite initializer

		self.image = data.pngs['explode_star1']
		self.rect = self.image.get_rect()
		self.rect.move_ip( position )

		self.displayRect = self.rect.move(0,0)

		self.counter = 0

	#---------------------------------------------------------------------
	def NotifyDirtyScreen(self, bgMangr ):
		pass

	#----------------------------------------------------------------------
	def update(self):
		self.counter += 4

		if self.counter >= 254:
			self.kill()
			return

		self.image.set_alpha( 255 - (self.counter +2) )

#------------------------------------------------------------------------------
class Spark(pygame.sprite.Sprite):
	def __init__(self, position):
		pygame.sprite.Sprite.__init__(self) #call Sprite initializer
	
		self.image = pygame.Surface( (2,2) )
		self.color = ( rng.randint( 100,255),
		               rng.randint( 100,255),
		               rng.randint( 100,255),
		             )
		self.movement = [ rng.randint(-3,3), rng.randint(-1,2) ]
		self.blinktime = rng.randint(1,4)
		self.blinkCounter = 0

		self.image.fill( self.color )
		self.rect = self.image.get_rect()
		self.rect.center = position

	#----------------------------------------------------------------------
	def update(self):
		self.blinkCounter = (self.counter + 1) % self.blinktime
		self.rect.move_ip( self.movement )

		if not self.blinkCounter:
			self.image.fill( (0,0,0,0) )
		else:
			self.image.fill( self.color )

#------------------------------------------------------------------------------
class SparkleEffect(pygame.sprite.Sprite):
	def __init__(self, position):
		pygame.sprite.Sprite.__init__(self) #call Sprite initializer
	
		size = (100,100)
		self.image = pygame.Surface( size )
		self.counter = 0
		self.duration = 300

		self.image.fill( (0,0,0,0) )
		self.rect = self.image.get_rect()
		self.rect.center = position

		self.sparks = []
		for i in range(10):
			self.sparks.append(Spark( (size[0]/2,size[1]/2) ))
		self.displayRect = self.rect.move(0,0)

	#---------------------------------------------------------------------
	def NotifyDirtyScreen(self, bgMangr ):
		pass

	#----------------------------------------------------------------------
	def update(self):
		self.counter += 1
		if self.counter > self.duration:
			self.kill()
			return

		self.image.fill( (0,0,0,0) )
		for spark in self.sparks:
			spark.update()
			self.image.blit( spark.image, spark.rect )

		
#------------------------------------------------------------------------------
class VisualEffectManager:
	#----------------------------------------------------------------------
	def __init__(self, spriteGroup):
		self.spriteGroup = spriteGroup
		self.kinds = {
		              'explosion': Explosion,
		              'flash': FlashEffect,
		              'sparkle': SparkleEffect,
		             }
	
	#----------------------------------------------------------------------
	def PlayEffect(self, effectName, position):
		e = self.kinds[effectName]( position )
		self.spriteGroup.add( e )

