"""
events.py
---------
This is a weird module and uses difficult to read code to make an event
broker with the minimum of typing.  Basically whenever an event is created, 
it is automatically broadcast using the module-level function, EventFired()

Note: this is much less sophisticated than an EventManager (as in sjbeasts
and my tutorial).  In particular, it suffers from the ABC->ACB event "out of
order" phenomenon and doesn't use weakrefs, so it keeps all listeners 
unessecarily alive.

It's only advantage is that it saves me some typing.

For the Glarf project these events are only used for special effects and stuff
ie, non-mission-critical things.
"""
#------------------------------------------------------------------------------
# Module-Level stuff
#------------------------------------------------------------------------------
from log import log

#outside objects can feel free to add themselves to this list
#YES, it is pretty lazy.  Bad programmer!  No cookie!
__listeners = []

__validEvents = []

def AddListener( newListner ):
	__listeners.append( newListner )

def AddEvent( newEvent ):
	__validEvents.append( newEvent )
	
def Fire( evName, *args, **kwargs ):
	#NOTE: by just taking the evName as a string, this won't be checked
	#      at load-time, it will be checked at runtime.  Load-time would
	#      be preferred, but I'm lazy and these events are unimportant
	#      (only for special effects and the like)

	# run-time check. looks in the module-level globals for the named event
	if evName not in __validEvents + globals().keys():
		raise Exception( "event not defined" )

	log.info( 'firing event' + str( evName ) )
	for listener in __listeners:
		methodName = "On_"+ evName
		#if the listener has a method that can handle this, call it
		try: 
			#get the method
			listnerMethod = getattr( listener, methodName)
			#call that method
			listnerMethod( *args, **kwargs )
		except:
			pass


#------------------------------------------------------------------------------
class Event:
	"""this is a superclass for any events that might be generated by an
	object and sent to the EventManager"""
	def __init__(self):
		self.name = "Generic Event"
	def broadcast(self):
		pass
#------------------------------------------------------------------------------
class GUIEvent(Event): pass

class AnimationTickEvent(GUIEvent):
	def __init__(self):
		self.name = "Timed Animation Tick Event"


class GUIBlockEvent(GUIEvent):
	"""..."""
	def __init__(self):
		self.name = "Block GUI Events Pending Completion of some task"

class GUIUnBlockEvent(GUIEvent):
	"""..."""
	def __init__(self):
		self.name = "Unblock the GUI"

class GUIFocusNextWidgetEvent(GUIEvent):
	"""..."""
	def __init__(self, layer=0):
		self.name = "Activate the next widget Event"
		self.layer = layer

class GUIFocusPrevWidgetEvent(GUIEvent):
	"""..."""
	def __init__(self, layer=0):
		self.name = "Activate the previous widget Event"
		self.layer = layer

class GUIFocusThisWidgetEvent(GUIEvent):
	"""..."""
	def __init__(self, widget):
		self.name = "Activate particular widget Event"
		self.widget = widget

class GUIPressEvent(GUIEvent):
	"""..."""
	def __init__(self, layer=0):
		self.name = "All Active widgets get pressed Event"
		self.layer = layer

class GUIKeyEvent(GUIEvent):
	"""..."""
	def __init__(self, key, layer=0):
		self.name = "key pressed Event"
		self.key = key
		self.layer = layer

class GUIControlKeyEvent(GUIEvent):
	"""..."""
	def __init__(self, key):
		self.name = "Non-Printablekey pressed Event"
		self.key = key

class GUIClickEvent(GUIEvent):
	"""..."""
	def __init__(self, pos, layer=0):
		self.name = "Mouse Click Event"
		self.pos = pos
		self.layer = layer

class GUIMouseMoveEvent(GUIEvent):
	"""..."""
	def __init__(self, pos, layer=0):
		self.name = "Mouse Moved Event"
		self.pos = pos
		self.layer = layer

class GUICharactorSelectedEvent(GUIEvent):
	"""..."""
	def __init__(self, charactor, wipeOthers=1):
		self.name = "A Charactor has been selected by the user"
		self.charactor = charactor
		self.wipeOthers = wipeOthers


class GUICharactorUnSelectedEvent(GUIEvent):
	"""..."""
	def __init__(self, charactor):
		self.name = "A Charactor has been unselected by the user"
		self.charactor = charactor

class GUIChangeScreenRequest(GUIEvent):
	"""..."""
	def __init__(self, key):
		self.name = "Change the active GUI to the one referenced by key"+str(key)
		self.key = key


class GUIDialogAddRequest(GUIEvent):
	"""..."""
	def __init__(self, key, msg=""):
		self.name = "Add a new dialog on top"
		self.key = key
		self.msg = msg

class GUIDialogRemoveRequest(GUIEvent):
	"""..."""
	def __init__(self, key):
		self.name = "Remove a new dialog from the top"
		self.key = key

class GUIScrollRequest(GUIEvent):
	"""..."""
	def __init__( self, target, amount ):
		self.name = "Request to Scroll by certain amount"
		self.target = target
		self.amount = amount

class GUISelectItemEvent(GUIEvent):
	"""..."""
	def __init__( self, item ):
		self.name = "Select an Item"
		self.item = item

class LevelStartedEvent(Event): pass
	#pass
class LevelCompletedEvent(Event): pass
	#pass
class EnemyDeathEvent(Event): pass
	#def __init__( self, enemy, pos ):
		#self.enemy = enemy
		#self.pos = pos
class PowerupConsume(Event): pass
class CoinConsume(Event): pass
	#def __init__( self, powerup, pos ):
		#self.powerup = powerup
		#self.pos = pos
class GlarfDeath(Event): pass
	#def __init__( self, glarf, pos ):
		#self.glarf = glarf
		#self.pos = pos
class GlarfHurt(Event): pass
	#def __init__( self, pos ):
		#self.pos = pos
class MawJumperJumps(Event): pass
