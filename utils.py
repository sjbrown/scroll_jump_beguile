#!/usr/bin/env python
from pygame.locals import *
from log import log
import pygame

#-----------------------------------------------------------------------------
def allKUPs(x): 
	return x.type == KEYUP

#-----------------------------------------------------------------------------
def vectorSum ( a, b ):
	return [a[0]+b[0], a[1]+b[1]]


#-----------------------------------------------------------------------------
def load_animation(moduleName, animName='default'):
	anim = None
	moduleName = moduleName.lower()
	exec( 'from data.'+moduleName+'.chardef import '+animName )
	exec( 'anim = '+animName )
	anim.Reset()
	return anim

#-----------------------------------------------------------------------------
def stringToKey( theString ):
	if hasattr( pygame.constants, theString ):
		return getattr( pygame.constants, theString )

#-----------------------------------------------------------------------------
def Event( evName, *args, **kwargs ):
	"""Fire off an inconsequential event"""
	try:
		import events
		events.Fire( evName, *args, **kwargs )
	except Exception, details:
		#totally don't care if it doesn't work.  Even if the module
		#doesn't load, I don't care because these events are not
		#mission-critical
		log.info( 'failed to fire an event' )
		log.info( details )



#this calls the 'main' function when this script is executed
if __name__ == '__main__': print "didn't expect that!"
