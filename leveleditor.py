#!/usr/bin/env python
#Import Modules
import os, pygame, operator, math, string
from copy import copy
from inspect import isclass
from pygame.locals import *


from pygame.sprite import Group
from scrollGroup import ScrollSpriteGroup, IdlerSpriteGroup
from utils import *
from physics import *

RESOLUTION = (900,600)
#RESOLUTION = (1000,720)


from objects import *
from charactor_glarf import *
from scroll_bgmanager import SeamedBackgroundManager
import level1

from pygame.sprite import *
from pygame import Surface, Rect

from gui_widgets import *
import events

events.AddEvent( "SaveRequest" )
events.AddEvent( "PauseToggleRequest" )
events.AddEvent( "CloneRequest" )
events.AddEvent( "SnapToggleRequest" )

def calc_snaptogrid_pos( posX, posY, gridX, gridY ):
	"""Given an x,y position and a grid dimensions, calculate where
	that position should move to so that it's snapped snap to the grid."""
	offGridX = posX % gridX
	offGridY = posY % gridY
	if offGridX > gridX/2:
		xAdjust = gridX -offGridX
	else:
		xAdjust = -offGridX
	if offGridY > gridY/2:
		yAdjust = gridY-offGridY
	else:
		yAdjust = -offGridY
	return ( xAdjust, yAdjust )

#------------------------------------------------------------------------------
class LevelEditorDisplayer:
	activeLevel = None

	def __init__(self, bgMangr, musicMangr):
		self.isDone = 0
		self.replacementDisplayerClass= None
		self.levelDisplayer = None
		self.bgMangr = bgMangr
		self.dragging = 0

		if self.activeLevel != None:
			self.levelDisplayer = self.activeLevel

		events.AddListener( self )

		screen = self.bgMangr.screen

		self.edInterface = EditorInterface( screen )
		fauxWidth = screen.get_width()
		fauxHeight = screen.get_height() - self.edInterface.editPanel.rect.height
		self.fauxScreen = Surface( (fauxWidth, fauxHeight) )

		self.fauxBgMangr = SeamedBackgroundManager(self.fauxScreen)
		self.levelDisplayer.bgMangr = self.fauxBgMangr

		self.edInterface.SetLevel( self.levelDisplayer )
		self.edInterface.SetBackgroundManager( self.bgMangr )

	#----------------------------------------------------------------------
	def SignalKey( self, event, upKeys ):
		#TODO: is this ever called??
		self.levelDisplayer.SignalKey( event, upKeys )
		self.edInterface.Key(event)

	#----------------------------------------------------------------------
	def MouseDown( self, pos ):
		self.edInterface.MouseDown( pos )
	#----------------------------------------------------------------------
	def MouseUp( self, pos ):
		self.edInterface.MouseUp( pos )
	#----------------------------------------------------------------------
	def MouseOver( self, event ):
		self.edInterface.MouseOver( event )

	#----------------------------------------------------------------------
	def DoGraphics( self, screen, display, timeChange ):
		if not self.edInterface.levelPaused:
			self.levelDisplayer.triggerGroup.clear(screen)
			self.levelDisplayer.DoGraphics( self.fauxScreen, 
			                                pygame.display, 
			                                timeChange )
			changedRects =  self.levelDisplayer.triggerGroup.draw(
			                self.fauxScreen )
			pygame.display.update( changedRects )


		screen.blit( self.fauxScreen, self.fauxScreen.get_rect() )
		self.edInterface.DoGraphics(screen, pygame.display, timeChange)
		screen.blit( self.edInterface.editPanel.image, self.edInterface.editPanel.rect )
		pygame.display.flip()


#------------------------------------------------------------------------------
class EditorPanel(WidgetAndContainer):

	def __init__(self, screen):
		WidgetAndContainer.__init__(self, self, None)
		self.color = (0,100,0)

		self.image = Surface( (screen.get_width(), 100) )
		self.image.fill( self.color )
		self.rect = self.image.get_rect()
		self.rect.bottomleft = screen.get_rect().bottomleft


		self.internalGroup = RenderUpdates()
		self.toggler = 0

		self.iconSprite = Sprite()
		self.iconSprite.image = Surface( (100,100) )
		self.iconSprite.image.fill( self.color )
		self.iconSprite.rect = self.iconSprite.image.get_rect()
		self.internalGroup.add( self.iconSprite )

		self.nameLabel = LabelSprite( self, 'None' )
		self.nameLabel.rect.topleft = (120, 10)
		self.internalGroup.add( self.nameLabel )

		self.xLabel = LabelSprite( self, 'X' )
		self.xLabel.rect.topleft = (120, 40)
		self.internalGroup.add( self.xLabel )

		self.yLabel = LabelSprite( self, 'Y' )
		self.yLabel.rect.topleft = (120, 70)
		self.internalGroup.add( self.yLabel )

		self.xText = TextBoxSprite( self, 400 )
		self.xText.rect.topleft = (220, 40)
		self.internalGroup.add( self.xText )
		
		self.yText = TextBoxSprite( self, 400 )
		self.yText.rect.topleft = (220, 70)
		self.internalGroup.add( self.yText )

		self.palButton = ButtonSprite( self, 'Palette', 
		                               None, self.Palette )
		self.palButton.rect.topleft = (830, 30)
		self.internalGroup.add( self.palButton )

		self.sButton = ButtonSprite( self, 'Save', None, self.Save )
		self.sButton.rect.topleft = (660, 40)
		self.internalGroup.add( self.sButton )

		self.pButton = ButtonSprite( self, 'Pause', None, self.Pause )
		self.pButton.rect.topleft = (660, 60)
		self.internalGroup.add( self.pButton )

		self.snapButton = ButtonSprite( self, 
		                                'Snap To Grid', 
		                                None, self.ToggleSnap )
		self.snapButton.rect.topleft = (660, 80)
		self.internalGroup.add( self.snapButton )

		self.cButton = ButtonSprite( self, 'Clone', None, self.Clone )
		self.cButton.rect.topleft = (440, 10)

	#----------------------------------------------------------------------
	def ShowCloneButton(self):
		self.internalGroup.add( self.cButton )
	#----------------------------------------------------------------------
	def HideCloneButton(self):
		self.cButton.kill()
	
	#----------------------------------------------------------------------
	def Post( self, ev ):
		"""An event was posted by one of the widgets"""
		pass
	#----------------------------------------------------------------------
	def RegisterListener( self, listener ):
		pass
	#----------------------------------------------------------------------
	def Pause( self ):
		events.Fire( "PauseToggleRequest" )
	#----------------------------------------------------------------------
	def Clone( self ):
		events.Fire( "CloneRequest" )
	#----------------------------------------------------------------------
	def ToggleSnap( self ):
		events.Fire( "SnapToggleRequest" )
		
	#----------------------------------------------------------------------
	def Save( self ):
		events.Fire( "SaveRequest" )
	
	#----------------------------------------------------------------------
	def Palette( self ):
		print 'Palette...'
		print 'This does nothing.  TODO....'

	#----------------------------------------------------------------------
	def Click( self, pos ):
			ev = GUIClickEvent( (pos[0], pos[1]) )
			self.xText.Notify( ev )
			self.yText.Notify( ev )
			self.palButton.Notify( ev )
			self.sButton.Notify( ev )
			self.pButton.Notify( ev )
			self.cButton.Notify( ev )
			self.snapButton.Notify( ev )
			
			
	#----------------------------------------------------------------------
	def Show( self, theSprite ):
		self.selectedSprite = theSprite
		print "showing a sprite: ", theSprite
		#copy the sprite image to the icon sprite
		self.image.fill( self.color )
		self.iconSprite.image.fill( (0,100,100) )
		self.iconSprite.image.blit( theSprite.image, (0,0) )

		self.nameLabel.SetText( str(theSprite) )
		try:
			self.xText.SetText( str(theSprite.originalPos[0]) )
			self.yText.SetText( str(theSprite.originalPos[1]) )
		except AttributeError:
			self.xText.SetText( str(theSprite.rect.x) )
			self.yText.SetText( str(theSprite.rect.y) )
	
	#--------------------------------------------------------------------------
	def update(self):
		blackRectImg = Surface( self.rect.size )
		blackRectImg.fill( self.color )
		self.internalGroup.clear( self.image, blackRectImg )

		self.internalGroup.update( )

		changedRects =  self.internalGroup.draw(self.image)

#------------------------------------------------------------------------------
class EditorInterface:
	def __init__(self, screen):

		events.AddListener( self )

		self.levelPaused = 0
		self.dragging = 0
		self.snapToGrid = True
		self.gridSize = [8,8]

		self.temporaryGroup = RenderUpdates()
		self.toggler = 0
		self.mousePosAtSelect = [0,0]
		self.objPosAtSelect = [0,0]
		self.highlightedObj = None
		self.selectedSprite = None

		self.redRect = pygame.sprite.Sprite()
		self.greenRect = pygame.sprite.Sprite()

		self.editPanel = EditorPanel(screen)
		self.level = None
		self.bgMangr = None

	#----------------------------------------------------------------------
	def SetLevel( self, level ):
		self.level = level
	#----------------------------------------------------------------------
	def SetBackgroundManager( self, bgMangr ):
		self.bgMangr = bgMangr

	#----------------------------------------------------------------------
	def Key( self, event ):
		#TODO: this has nasty coupling of editPanel and the edInterface.
		ev = None

		theSprite = self.selectedSprite

		if event.type == KEYDOWN \
		  and event.key == K_RETURN :
			if self.editPanel.xText.focused:
				self.editPanel.xText.SetFocus(0)
				try:
					newVal = int( self.editPanel.xText.text )
				except:
					return
				try:
					origVal = theSprite.originalPos[0]
					theSprite.rect.move_ip(newVal-origVal,0)
				except AttributeError:
					theSprite.rect.x = newVal
			if self.editPanel.yText.focused:
				self.editPanel.yText.SetFocus(0)
				try:
					newVal = int( self.editPanel.yText.text )
				except:
					return
				try:
					origVal = theSprite.originalPos[1]
					theSprite.rect.move_ip(0,newVal-origVal)
				except AttributeError:
					theSprite.rect.y = newVal

		elif event.type == KEYDOWN :
			character = str(event.unicode)
			if character and character in string.printable:
				ev = GUIKeyEvent(character)
			elif event.key == K_BACKSPACE:
				ev = GUIControlKeyEvent( event.key )

		if ev:
			self.editPanel.xText.Notify( ev )
			self.editPanel.yText.Notify( ev )

	#----------------------------------------------------------------------
	def MouseOver( self, ev ):
		if self.dragging:
			self.DragTo( ev )
		else:
			self.Hover( ev )
	#----------------------------------------------------------------------
	def DragTo( self, ev ):
		physPos = ( ev.pos[0] + self.bgMangr.offset[0],
		            ev.pos[1] + self.bgMangr.offset[1] )

		xDiff = ev.pos[0] - self.mousePosAtSelect[0]
		yDiff = ev.pos[1] - self.mousePosAtSelect[1]

		workingObjRect = self.highlightedObj.rect

		workingObjRect.topleft = ( 
		                           self.objPosAtSelect[0] + xDiff, 
		                           self.objPosAtSelect[1] + yDiff )

		if self.snapToGrid:
			xAdjust, yAdjust = calc_snaptogrid_pos(
			           workingObjRect.x,
			           workingObjRect.y,
			           self.gridSize[0],
			           self.gridSize[1],
			                                      )
			workingObjRect.move_ip( xAdjust, yAdjust )
			

		#draw a green rectangle there.
		self.greenRect.rect = workingObjRect.move( (0,0) )
		self.greenRect.rect.move_ip( -self.bgMangr.offset[0],
		                             -self.bgMangr.offset[1] )
		self.greenRect.image = Surface( self.greenRect.rect.size )
		self.greenRect.image.fill( (0,255,0) )

		self.temporaryGroup.add( self.greenRect )



	#----------------------------------------------------------------------
	def Hover( self, ev ):
		physPos = ( ev.pos[0] + self.bgMangr.offset[0],
		            ev.pos[1] + self.bgMangr.offset[1] )

		self.temporaryGroup.empty()

		solids = self.level.solids

		# don't try to pass the event through if it occurred inside
		# the gui element container
		if ev.pos[1] > self.editPanel.rect.y:
			return

		# find the sprite where the mouse clicked
		collider = None
		for s in solids.sprites():
			if s.rect.collidepoint( physPos ):
				collider = s
				break
		if not collider:
			return

		#draw a red rectangle there.
		self.redRect.rect = collider.rect.move( -self.bgMangr.offset[0],
		                                        -self.bgMangr.offset[1] )
		self.redRect.image = Surface( self.redRect.rect.size )
		self.redRect.image.fill( (255,0,0) )

		self.temporaryGroup.add( self.redRect )


	#----------------------------------------------------------------------
	def MouseDown( self, pos ):
		self.mouseDownPos = pos

		if self.editPanel.rect.collidepoint( pos ):
			return

		collider = self.MouseSelect( pos )
		if collider:
			self.dragging = 1

	#----------------------------------------------------------------------
	def MouseUp( self, pos ):
		self.dragging = 0
		amountMoved = abs(pos[0] - self.mouseDownPos[0]) + \
		              abs(pos[1] - self.mouseDownPos[1])
		if amountMoved < 10:
			#we moved less than 10 pixels, therefore its a click
			self.Click(pos)
			print "didn't mean to drag my highlighted object"
			self.highlightedObj = None
		else:
			self.MouseDrop( pos )
			
	#----------------------------------------------------------------------
	def Click( self, pos ):
		
		ePanelRect = self.editPanel.rect
		
		if ePanelRect.collidepoint( pos ):
			#the click happened inside the gui element container
			newPos = ( pos[0] - ePanelRect.x, pos[1] - ePanelRect.y )
			self.editPanel.Click( newPos )
			


	#----------------------------------------------------------------------
	def MouseDrop( self, pos ):
		if not self.highlightedObj:
			return

		xDiff = pos[0] - self.mousePosAtSelect[0]
		yDiff = pos[1] - self.mousePosAtSelect[1]

		print "dropping my highlighted object"
		self.highlightedObj.rect.topleft = ( 
		                               self.objPosAtSelect[0] + xDiff, 
		                               self.objPosAtSelect[1] + yDiff )

		if self.snapToGrid:
			xAdjust, yAdjust = calc_snaptogrid_pos(
			           self.highlightedObj.rect.x,
			           self.highlightedObj.rect.y,
			           self.gridSize[0],
			           self.gridSize[1],
			                                      )
			self.highlightedObj.rect.move_ip( xAdjust, yAdjust )

		self.highlightedObj = None

	#----------------------------------------------------------------------
	def MouseSelect( self, pos ):
		"""Try to select an object at the given position.  Return
		   the colliding object, or None if there was nothing there"""

		physPos = ( pos[0] + self.bgMangr.offset[0],
		            pos[1] + self.bgMangr.offset[1] )

		solids = self.level.solids

		# find the sprite where the mouse clicked
		collider = None
		for s in solids.sprites():
			if s.rect.collidepoint( physPos ):
				collider = s
				break
		if not collider:
			return None

		self.highlightedObj = collider
		print "got a highlighted object to drag:", collider
		self.mousePosAtSelect = pos
		self.objPosAtSelect = collider.rect.topleft

		self.Show( collider )

		if hasattr( collider, 'Clone' ):
			self.editPanel.ShowCloneButton()
			
		else:
			self.editPanel.HideCloneButton()
			

		return collider

	#----------------------------------------------------------------------
	def On_CloneRequest( self ):
		print "cloning ", self.selectedSprite
		self.selectedSprite.Clone()
	#----------------------------------------------------------------------
	def On_PauseToggleRequest( self ):
		print 'Toggling Pause...'
		self.levelPaused = not self.levelPaused
	#----------------------------------------------------------------------
	def On_SnapToggleRequest( self ):
		print 'Toggling Snap To Grid...'
		self.snapToGrid = not self.snapToGrid
	#----------------------------------------------------------------------
	def On_SaveRequest( self ):
		print 'SAVING...'
		import shutil
		shutil.copy( os.curdir + '/data/level1/level.py', os.tmpnam() )
		self.level.Save( os.curdir + '/data/level1/level.py' )		
		
	#----------------------------------------------------------------------
	def Show( self, theSprite ):
		self.selectedSprite = theSprite
		print "showing a sprite: ", theSprite
		self.editPanel.Show( theSprite )
		

	#---------------------------------------------------------------------
	def DoGraphics( self, screen, display, timeChange ):
		changedRects = self.editPanel.update()
		
		display.update( changedRects )
		
		#this is what does the flashing rectangles.
		if self.toggler == 1:
			self.toggler = 0
		else:
			self.toggler = 1
			self.temporaryGroup.update( )
			changedRects = self.temporaryGroup.draw(screen)
			display.update( changedRects )


			
	
#-----------------------------------------------------------------------------
def main():
	"""this function is called when the program starts.
	   it initializes everything it needs, then runs in
	   a loop until the function returns."""
	#Initialize Everything
	global screen
	screen = None
	pygame.init()
	screen = pygame.display.set_mode(RESOLUTION)
	pygame.display.set_caption('ScrollJB Level Editor')
	#pygame.mouse.set_visible(0)


	#Create The Backgound

	edInterface = EditorInterface( screen )
	fauxScreen = Surface( (screen.get_width(), 
	                       screen.get_height() - edInterface.editPanel.rect.height) )

	bgMangr = SeamedBackgroundManager(fauxScreen)
	#Display The Background
	fauxScreen.blit(bgMangr.GetBackground(), (0, 0))
	pygame.display.flip()

	clock = pygame.time.Clock()

	from main import MusicManager
	musicMangr = MusicManager()


	try:
		#load level based on string
		levelString = sys.argv[1]
		tmpGlobals = {}
		tmpLocals = {}
		execfile( levelString, tmpGlobals, tmpLocals )
		level = tmpLocals['GameLevel'](bgMangr, musicMangr)
	except:
		level = level1.GameLevel(bgMangr, musicMangr)

	edInterface.SetLevel( level )
	edInterface.SetBackgroundManager( bgMangr )

	oldfps = 0
	#Main Loop
	while 1:
		timeChange = clock.tick(40)
		newfps = int(clock.get_fps())
		if newfps != oldfps:
			#print "fps: ", newfps
			oldfps = newfps

		#Handle Input Events
		remainingEvents = pygame.event.get()
		for event in remainingEvents:
			upKeys = filter( allKUPs, remainingEvents )
			if event.type == MOUSEBUTTONDOWN:
				edInterface.MouseDown( event.pos )
			if event.type == MOUSEBUTTONUP:
				edInterface.MouseUp( event.pos )
			if event.type == MOUSEMOTION:
				edInterface.MouseOver( event )
			if event.type == QUIT:
				return
			elif event.type == KEYDOWN and event.key == K_ESCAPE:
				return
			elif event.type == KEYDOWN or event.type == KEYUP:
				level.SignalKey( event, upKeys )
				edInterface.Key( event )

		#Draw Everything

		if not edInterface.levelPaused:
			level.DoGraphics( fauxScreen, 
			                  pygame.display, 
			                  timeChange )

		screen.blit( fauxScreen, fauxScreen.get_rect() )
		edInterface.DoGraphics( screen, pygame.display, timeChange )
		screen.blit( edInterface.editPanel.image, edInterface.editPanel.rect )
		pygame.display.flip()



	#Game Over
	pygame.quit()


#this calls the 'main' function when this script is executed
if __name__ == '__main__': 
	print "Drag and Drop with the mouse"
	main()
