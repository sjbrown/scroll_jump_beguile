from dyn_cache import PngLoader, OggLoader, StringPngLoader, SmallStringPngLoader, WeaponIconLoader
import os

pngs = PngLoader()
weaponIcons = WeaponIconLoader()
oggs = OggLoader()
stringPngs = StringPngLoader()
smallStringPngs = SmallStringPngLoader()


from gameprofile import gameProfile
from userprofile import userProfile

if not userProfile.has_key( 'up' ):
	userProfile['up'] = 'K_UP'
if not userProfile.has_key( 'down' ):
	userProfile['down'] = 'K_DOWN'
if not userProfile.has_key( 'right' ):
	userProfile['right'] = 'K_RIGHT'
if not userProfile.has_key( 'left' ):
	userProfile['left'] = 'K_LEFT'
if not userProfile.has_key( 'fire' ):
	userProfile['fire'] = 'K_a'
if not userProfile.has_key( 'jump' ):
	userProfile['jump'] = 'K_SPACE'
