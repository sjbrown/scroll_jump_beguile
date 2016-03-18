#!/usr/bin/env python
#Import Modules
#import SiGL
import os, pygame, operator, math
from copy import copy
from inspect import isclass
from pygame.locals import *
from pygame.sprite import Group
from scrollGroup import ScrollSpriteGroup, IdlerSpriteGroup

from log import log
from utils import *
from physics import *

RESOLUTION = (800,600)


from objects import *
from scroll_bgmanager import SeamedBackgroundManager
from mainmenu import MainMenu, QuitScreen


#-----------------------------------------------------------------------------
class MusicManager:
	def __init__(self):
		self.currentSong = None

	def PlaySong( self, song ):
		if self.currentSong:
			self.currentSong.fadeout( 1200 )

		if type(song) == type(''): #is it a string?
			self.currentSong = pygame.mixer.Sound( song )
		else: #else, it should be a loaded song object
			self.currentSong = song

		self.currentSong.play( -1 ) #loops indefinitely

	
#-----------------------------------------------------------------------------
def main():
	"""this function is called when the program starts.
	   it initializes everything it needs, then runs in
	   a loop until the function returns."""
	#Attempt to optimize with psyco
	try:
		import psyco
		psyco.full()
	except Exception, e:
		print "no psyco for you!", e


	#Initialize Everything
	global screen
	screen = None
	pygame.init()
	screen = pygame.display.set_mode(RESOLUTION)
	pygame.display.set_caption('Glarf')
	#pygame.mouse.set_visible(0)

	#Create The Backgound
	bgMangr = SeamedBackgroundManager(screen)

	#Display The Background
	screen.blit(bgMangr.GetBackground(), (0, 0))
	pygame.display.flip()

	#Prepare Game Objects
	clock = pygame.time.Clock()

	musicMangr = MusicManager()

	displayer  = MainMenu(bgMangr, musicMangr)

	#Main Loop
	oldfps = 0
	while 1:
		timeChange = clock.tick(40)
		newfps = int(clock.get_fps())
		#if newfps != oldfps:
			#print "fps: ", newfps
			#oldfps = newfps

		#Handle Input Events
		remainingEvents = pygame.event.get()
		for event in remainingEvents:
			upKeys = filter( allKUPs, remainingEvents )
			if event.type == QUIT:
				return
			elif event.type == KEYDOWN and event.key == K_ESCAPE:
				return
			elif event.type == KEYDOWN or event.type == KEYUP:
				#if len(upKeys) > 0:
					#print upKeys 
				displayer.SignalKey( event, upKeys )
			elif event.type == MOUSEBUTTONDOWN:
				displayer.MouseDown( event.pos ) 
			elif event.type == MOUSEBUTTONUP:
				displayer.MouseUp( event.pos )
			elif event.type == MOUSEMOTION:
				displayer.MouseOver( event )

	#Draw Everything

		displayer.DoGraphics( screen, pygame.display, timeChange )

		# if the displayer is done, it's time to switch to 
		# a different displayer.  Sometimes the displayer doesn't
		# know what should come after it is done.
		# If we can't figure it out, default to the Main Menu
		if displayer.isDone:
			log.debug( "DISPLAYER IS DONE" )
			#if the displayer was the quit screen, we should quit
			if isinstance( displayer, QuitScreen ):
				break

			# clear out the old blitted image
			bgMangr.GetBgSurface(screen, screen.get_rect())
			pygame.display.flip()

			nextDisplayer = displayer.replacementDisplayerClass
			if isclass( nextDisplayer ):
				displayer = nextDisplayer(bgMangr, musicMangr)
			else:
				displayer = MainMenu(bgMangr, musicMangr)



	#Game Over
	print "Game is over"

	try:
		from data import userprofile
		userprofile.Save()
	except Exception, details:
		log.error( "Could not save preferences" )
		log.error( details )

	pygame.quit()

#this calls the 'main' function when this script is executed
if __name__ == '__main__': main()
