"""
Original Authour: Shandy Brown
License: Public Domain
"""
import os
import ConfigParser

# Use your project name here:
projectName = "glarf"

# The "main" section in the preferences file.  No need to change this.
section = 'global'

# Everything will be put into the gameProfile dict
gameProfile = {}


from userprofile import Dict2ConfigParser, WriteProfile

def Save():
	WriteProfile( gameProfile, section )


# If the HOME dir wasn't found, default to the current working dir
gameProfile['homeDir'] = os.getcwd()
# ~/.projectName/ directory
gameProfile['prefDir'] = gameProfile['homeDir']
# ~/.projectName/preferences file
gameProfile['prefFile'] = os.path.join(gameProfile['prefDir'], 'gameProfile' )


parser = ConfigParser.SafeConfigParser()
parser.read( gameProfile['prefFile'] )


def default_name():
	return projectName

def default_version():
	try:
		fp = file(os.path.join( gameProfile['prefDir'], 'VERSION' ))
		v = fp.read()
		fp.close
		return v
	except:
		return '0.30'

def default_goodbyeURL():
	return 'http://sjbrown.users.geeky.net/w/Glarf?action=AttachFile&amp;do=get&amp;target=glarf.png'

def default_homeURL():
	return 'http://sjbrown.users.geeky.net/w/Glarf'


# this checks some common keyboard controls, as well as 'username' and 'online'
for pref in ['version', 'homeURL', 'goodbyeURL']:
	try:
		gameProfile[pref] = parser.get( section, pref )
	except:
		#if it wasn't in the preferences file, see if we 
		#can load a default value using an above function
		#otherwise, just leave the pref unset.
		if locals().has_key( 'default_'+ pref ):
			gameProfile[pref] = locals()['default_'+pref]()



#
# at this point, gameProfile should be populated
#


#------------------------------------------------------------------------------
# Call it from the command line to test it
#------------------------------------------------------------------------------
if __name__ == "__main__":
	import sys
	from pprint import pprint
	pprint( gameProfile )
	try:
		if sys.argv[1] == '-w':
			#WriteProfile( gameProfile, section )
			Save()
	except:
		print 'use the -w flag to test writing'
