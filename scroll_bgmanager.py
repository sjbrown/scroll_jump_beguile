# Authour: Shandy Brown <sjb@ezide.com>
# License: LGPL
# Version: 0.1

#Import Modules
import os, pygame, operator, math
from copy import copy
from pygame.locals import *
from utils import *
import data

DEBUG = 1


#-----------------------------------------------------------------------------
class BackgroundManager:
	def __init__(self, screen):
		self.screen = screen
		self.image = data.pngs['backgr']
		self.rect = self.image.get_rect()
		self.offset = [0,0]
		self.dirty = 0
		self.newlyExposedArea = [ None, None ]
		screenRect = self.screen.get_rect()
		self.srcRect = Rect( self.offset[0], self.offset[1],
	                             screenRect.width, screenRect.height )


	#----------------------------------------------------------------------
	def BlitSelf( self, surface ):
		"""This is called when self.dirty is true and surface is usually
		the main pygame display surface"""
		self.srcRect.topleft =  self.offset[0], self.offset[1]
		surface.blit( self.image, (0,0), self.srcRect )

	#----------------------------------------------------------------------
	def GetBgSurface(self, drawToSurface, clearRect):
		"""This is the function that is normally passed to 
		RenderUpdates.clear as the "bgd" argument.  It gets passed
		the surface which we should draw to, and the rect which should
		be cleared"""
		#copy the clearRect
		offsetRect = clearRect.move(0,0)
		#move the offsetRect to my current offset
		offsetRect.topleft = vectorSum(offsetRect.topleft, self.offset)
		#blit to the target surface
		drawToSurface.blit( self.image, clearRect, offsetRect )

	#----------------------------------------------------------------------
	def GetBackground(self):
		return self.image

	#----------------------------------------------------------------------
	def RectIsOutOfBounds( self, physRect ):
		"""Returns a list indicating which parts of the physical rect
		are out of bounds. An empty result means the physical rect
		is not out of bounds."""
		result = []
		if physRect.left > self.rect.right:
			result.append( 'right' )
		if physRect.top > self.rect.bottom:
			result.append( 'bottom' )
		if physRect.right < self.rect.left:
		  	result.append( 'left' )
		if physRect.bottom < self.rect.top:
		  	result.append( 'top' )

		return result

	#----------------------------------------------------------------------
	def GetDisplayCenter( self, physRect ):
		return (physRect.centerx - self.offset[0], 
		        physRect.centery - self.offset[1] )

	#----------------------------------------------------------------------
	def GetOffsetScreenRect( self ):
		screenRect = self.screen.get_rect().move( self.offset[0],
		                                          self.offset[1] )
		return screenRect

	#----------------------------------------------------------------------
	def SpriteIsVisible( self, physRect ):
		screenRect = self.GetOffsetScreenRect()
		return screenRect.colliderect( physRect )


	#----------------------------------------------------------------------
	def CalculateNewlyExposedArea( self, oldOffset ):
		"""the newly exposed area is (at most) two rectangles:
		the exposed Y rect and the exposed X block
		note: a new algorithm will be needed if the screen
		      scrolls more than screenRect.width in one step"""

		#screenRect is the rect with the dimensions of the viewport
		screenRect = self.GetOffsetScreenRect()

		xBlockWidth = abs( self.offset[0] - oldOffset[0] )

		if oldOffset[0] < self.offset[0]:
			#new area exposed to the left
			xPos = screenRect.right - xBlockWidth 
		else:
			#new area exposed to the right
			xPos = self.offset[0]
		xBlock = Rect( xPos,
		               self.offset[1],
		               xBlockWidth,
		               screenRect.height )

		yBlockHeight = abs( self.offset[1] - oldOffset[1] )

		if oldOffset[1] < self.offset[1]:
			#new area exposed to the top
			yPos = screenRect.bottom - yBlockHeight
		else:
			#new area exposed to the bottom
			yPos = self.offset[1]
		yBlock = Rect( self.offset[0],
		               yPos,
		               screenRect.width, 
		               yBlockHeight )

		self.newlyExposedArea = [ xBlock, yBlock ]

	#----------------------------------------------------------------------
	def NotifyPlayerSpritePos( self, physRect ):
		"""Takes the rect of the sprite that the player is controlling 
		(the player's avatar) and determines if we need to scroll 
		the background
		By default, the center has 100 pixels of grace."""

		oldOffset = copy( self.offset )

		#screenRect is the rect with the dimensions of the viewport
		screenRect = self.GetOffsetScreenRect()
		self.dirty = 0

		#take the avatar's absolute position and get the on-screen pos
		avatarScreenLeft = physRect.left
		avatarScreenRight = physRect.right
		avatarScreenTop = physRect.top
		avatarScreenBottom = physRect.bottom

		#when in the center, the player can move 100 pixels in any
		#direction without scrolling happening.  This saves some 
		#processing and gives the game a pleasant feel
		leftScrollTrig = screenRect.centerx - 100
		rightScrollTrig = screenRect.centerx + 100
		topScrollTrig = screenRect.centery - 100
		bottomScrollTrig = screenRect.centery + 100

		minXOffset = self.rect.right
		maxXOffset = self.rect.left - screenRect.width
		minYOffset = self.rect.top
		maxYOffset = self.rect.bottom - screenRect.height

		if avatarScreenRight > rightScrollTrig \
		  and self.offset[0] != maxXOffset:
			self.offset[0] = min( maxXOffset,
			                      physRect.right - rightScrollTrig )
			self.dirty = 1
		elif avatarScreenLeft < leftScrollTrig \
		  and self.offset[0] != minXOffset:
			self.offset[0] = max( minXOffset,
			                      physRect.left - leftScrollTrig )
			self.dirty = 1

		if avatarScreenBottom > bottomScrollTrig \
		  and self.offset[1] != maxYOffset:
			self.offset[1] = min( maxYOffset,
			                      physRect.bottom-bottomScrollTrig )
			self.dirty = 1
		elif avatarScreenTop < topScrollTrig \
		  and self.offset[1] != minYOffset:
			self.offset[1] = max( minYOffset,
			                      physRect.top - topScrollTrig )
			self.dirty = 1

		if self.dirty:
			self.CalculateNewlyExposedArea( oldOffset )

		return self.GetDisplayCenter( physRect )

#-----------------------------------------------------------------------------
class SeamedBackgroundManager(BackgroundManager):
	def __init__(self, screen):
		BackgroundManager.__init__(self, screen)

		# seams are a list of lines (rects, really) where the current
		# background joins with another background
		# to set a One-Way seam, have it exist in part of the preceeding
		# background but not exist in any part of the sucsessive one
		self.seams = [
		 [ 'backgr','backgr2', Rect( 2980,699, 900, 2 ) ],
		 [ 'backgr2','backgr3', Rect( 2979,800, 2, 900 ) ]
		]

		self.bgPositions = {
				    'backgr': [0,0],
				    'backgr2': [2980,700],
				    'backgr3': [-900,800],
				   }

		self.backgrounds = {
				    'backgr': [self.image,self.rect],
				   }

		self.currentBg = 'backgr'
		
	#----------------------------------------------------------------------
	def LoadBackground( self, fname ):
		if self.backgrounds.has_key( fname ):
			return

		img = data.pngs[fname]
		rect = img.get_rect()
		rect.move_ip( *self.bgPositions[fname] )
		self.backgrounds[ fname ] = [img, rect]
		#print 'just loaded', img, rect

	#----------------------------------------------------------------------
	def BlitSelf( self, surface ):
		"""This is called when self.dirty is true and surface is usually
		the main pygame display surface"""
		screenRect = self.GetOffsetScreenRect()

		for name, bg in self.backgrounds.items():
			bgImg = bg[0]
			bgRect = bg[1]
			if screenRect.colliderect( bgRect ):
				clipRect = screenRect.clip( bgRect )
				x = clipRect.x - self.offset[0]
				y = clipRect.y - self.offset[1]
				clipRect.x -= bgRect.x
				clipRect.y -= bgRect.y
				surface.blit( bgImg, (x,y), clipRect )
				if DEBUG:
					for seam in self.seams:
						img = pygame.Surface( [seam[2][2], seam[2][3]])
						img.fill( (255,0,0) )
						x,y = seam[2][0], seam[2][1]
						x -= self.offset[0]
						y -= self.offset[1]
						surface.blit( img, (x,y) )

	#----------------------------------------------------------------------
	def GetBgSurface(self, drawToSurface, clearRect):
		"""This is the function that is normally passed to 
		RenderUpdates.clear as the "bgd" argument.  It gets passed
		the surface which we should draw to, and the rect which should
		be cleared"""

		#The clearRect portion of drawToSurface has junk on it.
		#We are expected to paint over the junk with the background.
		#The background could be part of any of the stitched bgs, or
		#it could be outside the bounds and therefore it should be
		#black.

		screenRect = self.GetOffsetScreenRect()

		#copy the clearRect and move the rectToClear to 
		#my current offset
		rectToClear = clearRect.move(screenRect.x,screenRect.y)

		if not rectToClear.colliderect( screenRect ):
			#print 'dont need to clear'
			return

		for name, bg in self.backgrounds.items():
			bgImg = bg[0]
			bgRect = bg[1]
			if rectToClear.colliderect( bgRect ):

				#intersect is the intersection of the screenRect
				#(remember that screenRect is in the physical
				# frame of reference, not the screen F.O.R.)
				#and the particular background we're painting
				intersect = rectToClear.clip( bgRect )

				#we don't want to blit the clipped bg 
				#img section to the entire clear rect for cases
				#when the clearRect crosses the boundary of
				#two backgrs - it would cause the last blitted
				#bg to write overtop of the preceeding
				clearArea = clearRect.clip( intersect.move(-screenRect.x, -screenRect.y))

				#next, shift the intersect so that we grab
				#the correct segment of the background image
				intersect.x -= bgRect.x
				intersect.y -= bgRect.y

				drawToSurface.blit( bgImg, clearArea, intersect)

	#----------------------------------------------------------------------
	def RectIsOutOfBounds( self, physRect, debug=0 ):
		if debug:
			print "In the debug version", debug

		#first, find the seams that intersect with the current screen
		collideSeams = self.GetSeamsThatCurrentlyCollide( debug )

		#get the background rects that are possibly onscreen
		#TODO: this implementation is overzealous.  fix.
		intersectingRects = []
		for img, rect in self.backgrounds.values():
			intersectingRects.append( rect )


		#assume it's all out of bounds at first
		result = ['top', 'right', 'bottom', 'left']

		def tryRemove( theList, item ):
			try:
				theList.remove( item )
			except ValueError:
				#list item was already removed
				pass

		#if debug:
			#print 'collideseams: ', collideSeams
			#print 'inters. rects: ', intersectingRects
		for bgRect in intersectingRects:
			#if debug:
				#print bgRect, physRect
			if len(result) == 0:
				break

			if bgRect.collidepoint( physRect.topleft ):
				tryRemove( result, 'top' )
				tryRemove( result, 'left' )
			if bgRect.collidepoint( physRect.topright ):
				tryRemove( result, 'top' )
				tryRemove( result, 'right' )
			if bgRect.collidepoint( physRect.bottomright ):
				if debug:
					print 'removing bottom'
				tryRemove( result, 'bottom' )
				tryRemove( result, 'right' )
			if bgRect.collidepoint( physRect.bottomleft):
				if debug:
					print 'removing bottom'
				tryRemove( result, 'bottom' )
				tryRemove( result, 'left' )

		#print 'bounds out: ', result
		#print 'bottom still in? ', 'bottom' in result
		return result

	#----------------------------------------------------------------------
	def GetSeamsThatCurrentlyCollide( self, debug=0 ):
		# will also load the seam

		screenRect = self.GetOffsetScreenRect()

		collideSeams = []
		for sList in self.seams:
			fnameA, fnameB, rect = sList[0], sList[1], sList[2]
			#if debug:
				#print 'selfscreengetrect', self.screen.get_rect()
				#print 'offsets', self.offset[0], self.offset[1]
				#print 'screenrect', screenRect
				#print 'self.seams[x] rect', rect
			if screenRect.colliderect( rect ):
				#print 'they did collide'
				collideSeams += [fnameA, fnameB]
				self.LoadBackground( fnameA )
				self.LoadBackground( fnameB )

		return collideSeams

	#----------------------------------------------------------------------
	def GetOffsetBounds( self ):
		"""We want the furthest we can set our offset.  We only have a
		background image for a certain area, we don't want our screen
		to go beyond that area."""

		#TODO: analyse the efficiency of this function

		r = self.backgrounds[self.currentBg][1]
		screenRect = self.GetOffsetScreenRect()

		#first, find the seams that intersect with the current screen
		collideSeams = self.GetSeamsThatCurrentlyCollide()

		class OffsetBounds:
			minX = r.x
			maxX = r.right - screenRect.width
			minY = r.y
			maxY = r.bottom - screenRect.height
		offsetBounds = OffsetBounds()

		#if there's only one visible background, just return
		if not collideSeams:
			return offsetBounds

		accessibleRects = []
		for fname in collideSeams:
			accessibleRects.append( self.backgrounds[fname][1] )

		unionRect = r.unionall( accessibleRects )
		offsetBounds.minX = unionRect.x
		offsetBounds.maxX = unionRect.right - screenRect.width
		offsetBounds.minY = unionRect.y
		offsetBounds.maxY = unionRect.bottom - screenRect.height

		return offsetBounds

	#----------------------------------------------------------------------
	def NotifyPlayerSpritePos( self, physRect ):
		"""Takes the rect of the sprite that the player is controlling 
		(the player's avatar) and determines if we need to scroll 
		the background
		By default, the center has 100 pixels of grace."""

		#set the currently inhabited background
		for fname, sList in self.backgrounds.items():
			if sList[1].contains( physRect ):
				self.currentBg = fname
				break


		oldOffset = copy( self.offset )

		#screenRect is the rect with the dimensions of the viewport
		screenRect = self.GetOffsetScreenRect()
		self.dirty = 0

		#when in the center, the player can move 100 pixels in any
		#direction without scrolling happening.  This saves some 
		#processing and gives the game a pleasant feel
		leftScrollTrig = screenRect.centerx - 100
		rightScrollTrig = screenRect.centerx + 100
		topScrollTrig = screenRect.centery - 100
		bottomScrollTrig = screenRect.centery + 100

		offsetBounds = self.GetOffsetBounds()

		if physRect.right > rightScrollTrig \
		  and self.offset[0] != offsetBounds.maxX:
			self.offset[0] = min( offsetBounds.maxX,
			      self.offset[0]+ physRect.right - rightScrollTrig )
			self.dirty = 1
		elif physRect.left < leftScrollTrig \
		  and self.offset[0] != offsetBounds.minX:
			self.offset[0] = max( offsetBounds.minX,
			      self.offset[0]+ physRect.left - leftScrollTrig )
			self.dirty = 1

		if physRect.bottom > bottomScrollTrig \
		  and self.offset[1] != offsetBounds.maxY:
			self.offset[1] = min( offsetBounds.maxY,
			      self.offset[1]+ physRect.bottom-bottomScrollTrig )
			#if self.offset[1] == 400:
				#print 'just set to 400'
				#print 'offsetBounds.maxY', offsetBounds.maxY
				#print 'physrect.bottom', physRect.bottom
				#print 'bottomScrollTrig', bottomScrollTrig
				#print '2nd ard to min', self.offset[1]+ physRect.bottom-bottomScrollTrig
			self.dirty = 1
		elif physRect.top < topScrollTrig \
		  and self.offset[1] != offsetBounds.minY:
			self.offset[1] = max( offsetBounds.minY,
			      self.offset[1]+ physRect.top - topScrollTrig )
			self.dirty = 1

		if self.dirty:
			self.CalculateNewlyExposedArea( oldOffset )

		return self.GetDisplayCenter( physRect )

