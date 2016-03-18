from objects import *
from visual_effects import VisualEffectManager
from charactor_glarf import *
from utils import *
from mawjumper import MawJumper
import events


#-----------------------------------------------------------------------------
class Platform( SimpleSprite ):
	def __init__(self, level, pos, imgname):
		SimpleSprite.__init__(self, imgname)
		self.originalPos = pos
		self.level = level
		self.rect.move_ip( pos )
		self.rect.inflate_ip( -12, -6 )
	def SetLevel(self, level):
		self.level = level
	def GetSaveString(self):
		return str( self.rect.inflate(12,6).topleft ) +', ()'
	def Clone( self ):
		pos = (self.rect.x + 20, self.rect.y+20)
		newOne =  self.__class__( self.level, pos )
		newOne.SetLevel( self.level )
		self.level.AddPlatform( newOne )
		return newOne

#-----------------------------------------------------------------------------
class Platform1( Platform ):
	def __init__(self, level, pos):
		Platform.__init__(self, level, pos, 'plat1')
		

#-----------------------------------------------------------------------------
class Platform2( Platform ):
	def __init__(self, level, pos):
		Platform.__init__(self, level, pos, 'plat2')

#-----------------------------------------------------------------------------
class Platform3( Platform ):
	def __init__(self, level, pos):
		Platform.__init__(self, level, pos, 'plat3')

#-----------------------------------------------------------------------------
class TiledPlatform( Platform ):
	def __init__(self, level, pos, howMany ):
		import data
		pygame.sprite.Sprite.__init__(self)
		self.howMany = howMany
		sourceTile = data.pngs['mesa_plat_tile']
		sourceRect = sourceTile.get_rect()
		finalWidth = howMany*sourceRect.width
		self.image = pygame.Surface( (finalWidth, sourceRect.height) )
		xpos = 0
		for i in range( howMany ):
			self.image.blit( sourceTile, (xpos,0) )
			xpos += sourceRect.width

		self.rect = self.image.get_rect()
		self.displayRect = self.rect.move(0,0)

		self.level = level
		self.rect.move_ip( pos )
		self.rect.inflate_ip( -12, -6 )
	#---------------------------------------------------------------------
	def GetSaveString(self):
		return str( self.rect.inflate(12,6).topleft ) +', ('+\
		       str(self.howMany) +',)'
	#---------------------------------------------------------------------
	def Clone( self ):
		return self.__class__(self.level,self.originalPos,self.howMany)
		newOne =  self.__class__( self.level, 
		                          self.originalPos, 
		                          self.howMany )
		newOne.SetLevel( self.level )
		self.level.AddPlatform( newOne )
		return newOne

#-----------------------------------------------------------------------------
class GameLevel:
	def __init__(self, bgMangr, musicMangr):
		self.isDone = 0
		self.replacementDisplayerClass= None
		self.bgMangr = bgMangr

		musicMangr.PlaySong( data.oggs['glarf_main'] )
		#TODO: hack alert
		musicMangr.currentSong.set_volume( 0.5 )

		self.charGroup    = ScrollSpriteGroup(self.bgMangr)
		self.enemyGroup   = ScrollSpriteGroup(self.bgMangr)
		self.neutralGroup = ScrollSpriteGroup(self.bgMangr)
		self.triggerGroup = ScrollSpriteGroup(self.bgMangr)
		self.effectGroup  = ScrollSpriteGroup(self.bgMangr)
		self.idlers       = IdlerSpriteGroup(self.bgMangr)
		self.hudGroupLow  = pygame.sprite.RenderUpdates()
		self.hudGroupHi   = pygame.sprite.RenderUpdates()

		self.effects = VisualEffectManager( self.effectGroup )

		self.resurrect = 1

		self.solids = Group()
		self.listenKeys = {}


		self.timeSinceDeath = -1


		self.charactor = Charactor(self.bgMangr)
		self.charactor.SetLevel( self )
		self.charGroup.add( self.charactor )
		self.solids.add( self.charactor )

		self.hudInfo = CharactorHUD( )
		self.hudInfo.SetCharactor( self.charactor )
		self.hudInfo.UpdateAll()
		self.hudGroupHi.add( self.hudInfo )


		self.Load( os.curdir +'/data/level1/level.py' )
		events.AddListener( self )

	#---------------------------------------------------------------------
	def SpriteAdd(self, sprite, isSolid=1 ):
		self.neutralGroup.add( sprite )
		if isSolid:
			self.solids.add( sprite )

	#---------------------------------------------------------------------
	def AddPlatform(self, platform ):
		self.SpriteAdd( platform, 1 )
	#---------------------------------------------------------------------
	def AddSolidSprite(self, sprite ):
		self.SpriteAdd( sprite, 1 )
	#---------------------------------------------------------------------
	def AddUnsolidSprite(self, sprite ):
		self.SpriteAdd( sprite, 0 )
	#---------------------------------------------------------------------
	def AddTriggerZone(self, tZone):
		self.triggerGroup.add( tZone )

	#---------------------------------------------------------------------
	def SpriteBirth(self, sprite):
		self.idlers.remove( sprite )
		if isinstance( sprite, MawJumper ):
			self.enemyGroup.add( sprite )
		else:
			self.neutralGroup.add( sprite )

		self.solids.add( sprite )

		try:
			import eventmanager, events
			ev = events.SpriteBirth( sprite )
			eventmanager.instance().Post( ev )
		except:
			pass

	#---------------------------------------------------------------------
	def SpriteDeath(self, sprite):
		log.debug( "SpriteDeath for" + str( sprite ) )
		# if this was the player's Charactor that died, go to Main Menu
		if isinstance(sprite, Charactor):
			self.timeSinceDeath = 0
			sprite.kill()
			return

		if self.resurrect:
			sprite.kill()
			if sprite.Resurrect():
				self.idlers.add( sprite )
		else:
			sprite.kill()


	#---------------------------------------------------------------------
	def HasGoneIntoKillzone(self, sprite):
		return not self.safeBounds.colliderect( sprite.rect )

	
	#---------------------------------------------------------------------
	def SignalKey( self, event, remainingEvents ):
		if self.listenKeys.has_key( event.key ):
			self.listenKeys[event.key]()
		else:
			self.charactor.SignalKey( event )

	#---------------------------------------------------------------------
	def MouseDown( self, pos ):
		pass
	#---------------------------------------------------------------------
	def MouseUp( self, pos ):
		from leveleditor import LevelEditorDisplayer
		self.replacementDisplayerClass = LevelEditorDisplayer
		self.replacementDisplayerClass.activeLevel = self
		self.isDone = 1

	#---------------------------------------------------------------------
	def MouseOver( self, event ):
		pass

	#---------------------------------------------------------------------
	def Load( self, filename ):
		#here we used the string to dynamically import a module
		#this will allow me to make the function dynamic in the future
		#so I can make multiple levels just by making new Definition
		#files.
		#__import__('data.level1', globals(), locals(), ['definition'] )
		#from data.level1 import definition
		# no, let's just load a file object and exec it.
		fp = file( filename )
		exec fp
		definition = GameLevelDefinition
		self.resurrect = definition.resurrect
		self.safeBounds = Rect( definition.safeBounds )
		for classObj, pos, extra in definition.items:
			newInstance = classObj( self, pos, *extra )
			newInstance.SetLevel(self)
			if isinstance( newInstance, Crate ):
				self.solids.add( newInstance )
				self.idlers.add( newInstance )
			elif isinstance( newInstance, PowerUp ):
				self.solids.add( newInstance )
				self.neutralGroup.add( newInstance )
			elif isinstance( newInstance, MawJumper ) :
				self.solids.add( newInstance )
				self.idlers.add( newInstance )
			elif isinstance( newInstance, Platform ) :
				self.AddPlatform( newInstance )
			elif isinstance( newInstance, TriggerZone ) :
				self.AddTriggerZone( newInstance )

	#---------------------------------------------------------------------
	def Save( self, filename=None ):
		if filename == None:
			filename = os.tmpnam()
			print 'file name not specified.  using', filename

		try:
			fp = file( filename, 'w' )
		except Exception, message:
			sys.stderr.write( 'SAVE ERROR' )
			sys.stderr.write( message )
			return

		# we don't want duplicates, so make a set.
		wholeSetOfSprites = set( self.solids.sprites() +\
		                        self.idlers.sprites() +\
		                        self.triggerGroup.sprites() +\
		                        self.neutralGroup.sprites()
		                       )


		deleteList = []
		for sprite in wholeSetOfSprites:
			if isinstance( sprite, Charactor ):
				deleteList.append( sprite )
			from weapons import Bullet
			if isinstance( sprite, Bullet ):
				deleteList.append( sprite )
		for sprite in deleteList:
			wholeSetOfSprites.remove( sprite )


		fp.write( 'class GameLevelDefinition:\n' )
		fp.write( '\tresurrect='+ str(self.resurrect) +'\n' )
		fp.write( '\titems = [\n' )

		for sprite in wholeSetOfSprites:
			if hasattr( sprite, 'GetSaveString' ):
				saveString = sprite.GetSaveString()
			else:
				saveString = str(sprite.rect.topleft) +', ()'
			fp.write( '\t ['+ sprite.__class__.__name__ +\
			          ', '+ saveString +\
			          ', ],\n'
			        )

		fp.write( '\t]\n' )
		sB = self.safeBounds
		fp.write( '\tsafeBounds = ( %d, %d, %d, %d )\n' %\
		                          (sB.x,sB.y, sB.width, sB.height) )
		fp.close()
		
	#---------------------------------------------------------------------
	def DoGraphics( self, screen, display, timeChange ):
		self.charGroup.clear( screen )
		self.enemyGroup.clear( screen )
		self.idlers.clear( screen )
		self.neutralGroup.clear(screen)
		#self.triggerGroup.clear(screen)
		self.effectGroup.clear(screen)
		self.hudGroupLow.clear( screen, self.bgMangr.GetBgSurface )
		self.hudGroupHi.clear( screen, self.bgMangr.GetBgSurface )


		#KEEP IN MIND when thinking about the updates that some
		#sprites can change which group they're in due to a call to
		#group.update().  Thus, they can have their update() method
		#called twice

		#charGroup should update first to move the viewing area
		self.charGroup.update( timeChange=timeChange )
		#triggergroup might cause sprite births so it should go next
		self.triggerGroup.update( timeChange=timeChange )
		#idler update should go next to notify newly born sprites
		self.idlers.update()
		#enemy group must update after idlers so that newly born
		#sprites have their rectangles set properly
		self.enemyGroup.update( timeChange=timeChange )
		self.neutralGroup.update( timeChange=timeChange )
		self.effectGroup.update( )
		self.hudGroupLow.update( None )
		self.hudGroupHi.update( None )

		changedRects =  self.neutralGroup.draw(screen)
		#changedRects += self.triggerGroup.draw(screen)
		changedRects += self.charGroup.draw(screen)
		changedRects += self.enemyGroup.draw(screen)
		changedRects += self.effectGroup.draw(screen)
		changedRects += self.hudGroupLow.draw(screen)
		changedRects += self.hudGroupHi.draw(screen)
		display.update( changedRects )

		if self.timeSinceDeath > -1:
			self.timeSinceDeath += timeChange
			# if > 1.5 seconds...
			if self.timeSinceDeath > 1500:
				self.isDone = 1

	#---------------------------------------------------------------------
	def On_GlarfHurt( self, glarf, coords ):
		print "Event recognized: glarf hurt"
		data.oggs.ouch.play()
		self.hudInfo.UpdateAll()
		self.effects.PlayEffect( 'sparkle', coords )

	#---------------------------------------------------------------------
	def On_GlarfDeath( self, glarf, coords ):
		print "Event recognized: glarf death"
		data.oggs.ouch.play()

	#---------------------------------------------------------------------
	def On_CoinConsume( self, coin, coords ):
		print "Event recognized: COIN consume"
		snd_star = data.oggs.star
		snd_star.play()
		self.hudInfo.UpdateAll()

	#---------------------------------------------------------------------
	def On_PowerupConsume( self, pUp, coords ):
		print "Event recognized: powerup consume"
		snd_star = data.oggs.star
		snd_star.play()
		newSprite = pygame.sprite.Sprite()
		newSprite.image = data.weaponIcons[ pUp.weapon ]
		print "powerup consume sprite image done"
		newSprite.rect = newSprite.image.get_rect()
		newSprite.rect.center = (100,100)
		self.hudGroupHi.add( newSprite )
		self.hudInfo.UpdateAll()

