from copy import copy

#------------------------------------------------------------------------------
def triple2str( colorTriple ):
	red   = colorTriple[0]
	green = colorTriple[1]
	blue  = colorTriple[2]
	colorInt = red*16**4 + green*16**2 + blue

	colorHexStr = hex( colorInt )[2:]

	#zero padding might be needed...
	zeros = '0' * (6-len(colorHexStr))
	return zeros + colorHexStr

#------------------------------------------------------------------------------
def str2triple( colorString ):
	s1 = colorString[0:2]
	s2 = colorString[2:4]
	s3 = colorString[4:6]
	return [ int(s1, 16), int(s2, 16), int(s3, 16) ]



pureHues = []
for xPos in range(0,2):
	for ff00pair in [ [0,255], [255,0] ]:
		#increment up by 6 at a time
		for i in range( 0, 256, 6 ):
			triplet = copy(ff00pair)
			triplet.insert( xPos, i )
			pureHues.append( triple2str(triplet) )


if __name__ == "__main__":
	for cString in  pureHues:
		print cString, str2triple( cString )
