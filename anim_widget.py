import pygame
from pygame.locals import *

#------------------------------------------------------------------------------
class AnimatedWidget(pygame.sprite.Sprite):
	def __init__(self, animation ):
		pygame.sprite.Sprite.__init__(self)

		self.timeChangeAccumulator = 0
		self.dirty = 1
		self.animation = None

		self.offset = [0,0]

		self.SetAnimation( animation )

		#print self.animation
		frame = self.animation.GetCurrent()
		self.image = frame.image
		self.rect = self.image.get_rect()

	#----------------------------------------------------------------------
 	def kill(self):
		pygame.sprite.Sprite.kill(self)
		print "i remain in groups", self.groups()
		self.animation.SetFinishCallback( None )
		#TODO: why did i have this here in the first place?
		#del self.animation
		self.animation = None

	#----------------------------------------------------------------------
 	def SetAnimation(self, newAnim):
		if self.animation: 
			self.animation.SetFinishCallback( None )
		self.animation = newAnim
		self.animation.SetFinishCallback( self.AnimationFinished )

	#----------------------------------------------------------------------
 	def NextFrame(self):
		self.dirty = 1
		self.animation.next()

	#----------------------------------------------------------------------
	def update(self, timeChange):
		"""This will change self.image if the frame is new"""
		if not self.dirty:
			return

		diff = timeChange + self.timeChangeAccumulator - 22
		if diff > 0:
			self.NextFrame()
			self.timeChangeAccumulator = diff
		else:
			self.timeChangeAccumulator += timeChange


		frame = self.animation.GetCurrent()
		change = frame.GetOffset( self.offset )
		if change != [0.0]:
			import operator
			self.rect.move_ip( change )
			self.offset = map( operator.add, self.offset, change )
		self.image = frame.image
		
	#----------------------------------------------------------------------
 	def AnimationFinished(self):
		pass
			

if __name__ == "__main__":
	print "that was unexpected"
