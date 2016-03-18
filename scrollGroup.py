# Authour: Shandy Brown <sjb@ezide.com>
# License: LGPL
# Version: 0.1

from pygame.sprite import RenderUpdates

DEBUG = 1

#TODO: might be a good place for psyco??

class ScrollSpriteGroup(RenderUpdates):
	"""a sprite group that can draw and clear with update rectangles
	   The ScrollSpriteGroup is derived from the RenderUpdates group
	   and keeps track of all the areas drawn and cleared. 
	   This sprite group is intended for a game where the background
	   scrolls.  It must be constructed with a Background Manager
	   (bgMangr).  The Background Manager helps translate between
	   global position (including the parts of the game world that are
	   off-screen) and visible position."""
	def __init__( self, bgMangr ):
		RenderUpdates.__init__(self)
		self.bgMangr = bgMangr

	def add_internal( self, sprite ):
		RenderUpdates.add_internal( self, sprite )
		center = self.bgMangr.GetDisplayCenter(sprite.rect)
		sprite.displayRect.center = center

	def update_helper(self, s):
		center = self.bgMangr.GetDisplayCenter(s.rect)
		s.displayRect.center = center
		#if hasattr( s, 'weapon' ):
			#print 'calling debug version'
			#bounds = self.bgMangr.RectIsOutOfBounds(s.rect, 1)
		#else:
		bounds = self.bgMangr.RectIsOutOfBounds(s.rect, 0)
		if bounds and hasattr( s, 'NotifyOutOfBounds' ):
			s.NotifyOutOfBounds( bounds )
		if self.bgMangr.dirty:
			s.NotifyDirtyScreen( self.bgMangr )
	
	def update(self, *args, **kwargs):
		"""update(...)
		   call update for all member sprites

		   calls the update method for all sprites in the group.
		   passes all arguments are to the Sprite update function."""
		for s in self.spritedict.keys():
			s.update(*args, **kwargs)
			self.update_helper( s )


	def clear( self, drawToSurface ):
		if self.bgMangr.dirty:
			#there's no point in clearing things because we're
			#about to wipe the whole surface in update()
			return
		RenderUpdates.clear( self, drawToSurface, 
		                     self.bgMangr.GetBgSurface )
		

	def draw(self, surface):
		"""draw(surface)
		   draw all sprites onto the surface

		   Draws all the sprites onto the given surface. It
		   returns a list of rectangles, which should be passed
		   to pygame.display.update()"""
		if self.bgMangr.dirty:
			self.bgMangr.BlitSelf( surface )
		spritedict = self.spritedict
		surface_blit = surface.blit
		dirty = self.lostsprites
		self.lostsprites = []
		dirty_append = dirty.append
		for s, r in spritedict.items():
			#TODO: might be more efficient if we didn't blit
			#      the ones that are not on screen
			newrect = surface_blit(s.image, s.displayRect)
			if r is 0:
				dirty_append(newrect)
			else:
				if newrect.colliderect(r):
					dirty_append(newrect.union(r))
				else:
					dirty_append(newrect)
					dirty_append(r)
			spritedict[s] = newrect
		if self.bgMangr.dirty:
			self.bgMangr.dirty = 0
			return [self.bgMangr.rect]
		else:
			return dirty



class IdlerSpriteGroup(ScrollSpriteGroup):
	""" IdlerSpriteGroup
	this is for the Idler class of objects that don't do anything
	until they become visible on the screen.  That way, the CPU is not
	consumed by a bunch of sprites that aren't even visible yet."""
	def clear(self, drawToSurface ): pass
	def draw(self): return []
	def update(self):
		if self.bgMangr.dirty:
			for s in self.spritedict.keys():
				s.NotifyDirtyScreen( self.bgMangr )

