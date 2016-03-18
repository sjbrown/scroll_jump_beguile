#!/usr/bin/env python
#Import Modules
import os, pygame, operator, math
from copy import copy
from pygame.locals import *
from log import log

OPENGL=0
datadir = 'data'

#-----------------------------------------------------------------------------
def load_png(name, extradirs=None):
	if extradirs:
		fullname = os.path.join(datadir, extradirs, name)
	else:
		fullname = os.path.join(datadir, name)
	try:
		image = pygame.image.load(fullname)
		if image.get_alpha is None:
			image = image.convert()
		else:
			image = image.convert_alpha()
	except pygame.error, message:
		log.debug( ' Cannot load image: '+ fullname )
		log.debug( 'Raising: '+ str(message) )
		raise message
	return image
#-----------------------------------------------------------------------------
def load_png_gl(name):
	from SiGL import surface
	fullname = os.path.join('data', name)
	try:
		pygame_image = pygame.image.load(fullname)
		image = surface.convert(pygame_image)
	except pygame.error, message:
		log.debug( 'GL Cannot load image: '+ fullname )
		raise SystemExit, message
	return image

if OPENGL:
	load_png = load_png_gl


#-----------------------------------------------------------------------------
def load_sound(name, extradirs=None):
	if extradirs:
		fullname = os.path.join(datadir, extradirs, name)
	else:
		fullname = os.path.join(datadir, name)

	class NoneSound:
		def play(self): pass

	if not pygame.mixer or not pygame.mixer.get_init():
		return NoneSound()

	try:
		sound = pygame.mixer.Sound(fullname)
	except pygame.error, message:
		log.debug( 'Cannot load sound: '+ fullname )
		raise pygame.error, message
	return sound

#-----------------------------------------------------------------------------
def load_animation(moduleName, animName='default'):
	anim = None
	moduleName = moduleName.lower()
	exec( 'from data.'+moduleName+'.chardef import '+animName )
	exec( 'anim = '+animName )
	anim.Reset()
	return anim

#this calls the 'main' function when this script is executed
if __name__ == '__main__': print "didn't expect that!"
