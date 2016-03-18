"""
A way to get access to a userProfile that can be stored for future invocations
of the program.

Usage:
	import userprofile
	print userprofile.userProfile['username']
	userprofile.userProfile['lastScore'] = str( 9999 )
	userprofile.Save()

Original Authour: Shandy Brown
License: Public Domain
"""
import os
import ConfigParser

# Use your project name here:
projectName = "glarf"

# The "main" section in the preferences file.  No need to change this.
section = 'global'

# Everything will be put into the userProfile dict
userProfile = {}

#------------------------------------------------------------------------------
# Functions to write preferences file 
#------------------------------------------------------------------------------
def Dict2ConfigParser( theDict, theParser, sectionName, ignoreList ):
	"""Recursive function to convert a dict into a ConfigParser object"""
	theParser.add_section( section )
	for key in theDict.keys():
		if key in ignoreList:
			continue
		if type(theDict[key]) == str:
			theParser.set( sectionName, key, theDict[key] )
		elif type(theDict[key]) == dict:
			Dict2ConfigParser( theDict[key], theParser, 
			                   key, ignoreList )
		else:
			raise "Dict contains something other than strings"

def WriteProfile( theDict, section ):
	"""function to write the preferences to a ConfigParser-compatible file
	"""
	#TODO: catch exceptions (perhaps outside)

	#don't write these locations.  They're decided when the userprofile
	#module is loaded
	ignores = 'homeDir', 'prefDir', 'prefFile'

	parser = ConfigParser.SafeConfigParser()
	Dict2ConfigParser( theDict, parser, section, ignores )

	if not os.path.isdir( theDict['prefDir'] ):
		os.mkdir( theDict['prefDir'], 0755 )
	fp = file( theDict['prefFile'], 'w' )
	try:
		parser.write( fp )
	finally:
		fp.close()

def Save():
	print "Saving Profile"
	WriteProfile( userProfile, section )
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
# Functions to set some defaults if they are needed
#------------------------------------------------------------------------------
def default_firstTime():
	return "1"
def default_online():
	return "1"
def default_username():
	try:
		n = os.getenv('USER')
	except:
		try:
			n = os.getenv('USERNAME')
		except:
			n = 'anonymous'
	return n
#------------------------------------------------------------------------------
	


# Try to find out the path name for the user's HOME directory
# this can be tricky because different operating systems do it 
# in different ways
if os.path.exists( os.path.expanduser('~') ):
	userProfile['homeDir'] = os.path.expanduser('~')
elif os.path.exists( os.getenv( 'HOME','' ) ):
	userProfile['homeDir'] = os.getenv( 'HOME','' )
elif os.path.exists( os.getenv( 'USERPROFILE','' ) ):
	userProfile['homeDir'] = os.getenv( 'USERPROFILE' ) 
else:
	# If the HOME dir wasn't found, default to the current working dir
	userProfile['homeDir'] = os.getcwd()

# ~/.projectName/ directory
userProfile['prefDir'] = os.path.join(userProfile['homeDir'], '.'+ projectName)
# ~/.projectName/preferences file
userProfile['prefFile'] = os.path.join(userProfile['prefDir'], 'preferences' )


parser = ConfigParser.SafeConfigParser()
parser.read( userProfile['prefFile'] )


# this checks some common keyboard controls, as well as 'username' and 'online'
for pref in ['username','online','firstTime',
             'up','down','left','right','jump','fire']:
	try:
		userProfile[pref] = parser.get( section, pref )
	except:
		#if it wasn't in the preferences file, see if we 
		#can load a default value using an above function
		#otherwise, just leave the pref unset.
		if locals().has_key( 'default_'+ pref ):
			userProfile[pref] = locals()['default_'+pref]()



#
# at this point, userProfile should be populated
#


#------------------------------------------------------------------------------
# Call it from the command line to test it
#------------------------------------------------------------------------------
if __name__ == "__main__":
	import sys
	from pprint import pprint
	pprint( userProfile )
	try:
		if sys.argv[1] == '-w':
			#WriteProfile( userProfile, section )
			Save()
	except:
		print 'use the -w flag to test writing'
