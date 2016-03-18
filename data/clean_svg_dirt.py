#! /usr/bin/python
""" Often SVG files that are created by autotracing a scanned-in drawing or
a photograph have small dots and specks in them.  This script will go through
an SVG document and remove all paths that are smaller than a certain threshold.
It won't get all the dirt (particularly it won't work against very thin lines
that are longer than the threshold), but it is faster than scouring the drawing
by hand."""

# Some test content
content = '''
<path
   id="path2904"
   d="M 7.3041190,5.0556410 
C 7.3061190,5.0557040 7.3081190,5.0557630 7.3101190, 5.0558260 
C 7.3139615,5.0609481 7.3167765,5.0670347 7.3195875,5.0731252 
C 7.3166 190,5.0720347 7.3126544,5.0709126 7.3086544,5.0707867 
C 7.3078119,5.0657591 7.3059654,5.0607001 7.3041190,5.0556410 
L 7.3041190,5.0556410 z "
   class="fil3" />
'''
content = '''
<path
   id="path2904"
   d="M 7.3041190,5.0556410 
C 7.3078119,5.0657591 7.3059654,5.0607001 17.3041190,15.0556410 
L 7.3041190,5.0556410 z "
   class="fil3" />
'''


import re, sys
from xml.dom import minidom

THRESHOLD = 0.02

#------------------------------------------------------------------------
# Try to grab the command line arguments
#------------------------------------------------------------------------
try:
	fname = sys.argv[1]
	fp = file( fname )
	content = fp.read()
	fp.close
except:
	sys.stderr.write( "\n----\nCouldn't get input from cmd line arg" )

try:
	THRESHOLD = float(sys.argv[2])
except:
	sys.stderr.write( '''
	           ----
	           Couldn't get deletion size threshold from cmd line arg''' )


#------------------------------------------------------------------------
# The regular expressions
#------------------------------------------------------------------------
pattern = 'd="([^"]*)"'
p_d = re.compile( pattern, re.DOTALL | re.VERBOSE | re.IGNORECASE )

pattern = '[ml]\s* (?P<x>-?[0-9][0-9\.]*) \s*,\s*  (?P<y>-?[0-9][0-9\.]*)'
#pattern = '[ml]\s* (?P<x>-?[0-9][0-9\.]*) \s\s*  (?P<y>-?[0-9][0-9\.]*)'
p_ml = re.compile( pattern, re.DOTALL | re.VERBOSE | re.IGNORECASE )

pattern = '''s\s*       -?[0-9][0-9\.]*   \s*,\s*        -?[0-9][0-9\.]*
              \s* (?P<x>-?[0-9][0-9\.]*)  \s*,\s*  (?P<y>-?[0-9][0-9\.]*)'''
p_s = re.compile( pattern, re.DOTALL | re.VERBOSE | re.IGNORECASE )

pattern = '''c\s*       -?[0-9][0-9\.]*   \s*,\s*        -?[0-9][0-9\.]*
              \s*       -?[0-9][0-9\.]*   \s*,\s*        -?[0-9][0-9\.]*
              \s* (?P<x>-?[0-9][0-9\.]*)  \s*,\s*  (?P<y>-?[0-9][0-9\.]*)'''
p_c = re.compile( pattern, re.DOTALL | re.VERBOSE | re.IGNORECASE )



#------------------------------------------------------------------------
# Go through the SVG document and remove the specks
#------------------------------------------------------------------------

dom = minidom.parseString(content)
allPaths = dom.getElementsByTagName("path")

numRemovals = 0
for path in allPaths:
	pString = path.toxml()
	dString = p_d.search( pString ).group(1)
	#print dString
	try:
		xPoints = []
		yPoints = []
		mXY = p_ml.findall( dString )
		sXY = p_s.findall( dString )
		cXY = p_c.findall( dString )
		for match in mXY:
			xPoints.append( float(match[0]) )
			yPoints.append(float(match[1]) )
		for match in sXY:
			xPoints.append( float(match[0]) )
			yPoints.append(float(match[1]) )
		for match in cXY:
			xPoints.append( float(match[0]) )
			yPoints.append(float(match[1]) )

		minX = min(xPoints)
		maxX = max(xPoints)
		minY = min(yPoints)
		maxY = max(yPoints)

		width = maxX - minX
		height = maxY - minY

		#print 'mXY ', mXY
		#print 'sXY ', sXY
		#print 'cXY ', cXY
		#print 'xpoints ', xPoints
		#print 'width = ', width, '(', maxX, '-', minX, ')'
		#print 'height = ', height, '(', maxY, '-', minY, ')'


		if width < THRESHOLD or height < THRESHOLD:
			#remove the node
			#print dString
			#print 'removing', numRemovals; numRemovals += 1
			path.parentNode.removeChild( path )

	except:
		sys.stderr.write( "\n----\nCouldn't process path:\n" )
		sys.stderr.write( pString )


# Write it out to output.svg
outfile = sys.stdout
dom.writexml( outfile )
	
