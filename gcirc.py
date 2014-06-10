import math

def gcirc(ra1,dc1,ra2,dc2):
    """
    Input values need to be all in decimal degrees, same epoch
    """

    # convert to floats
    ra1,dc1,ra2,dc2 = map(float,(ra1,dc1,ra2,dc2))

    d2r    = math.pi / 180.0
    as2r   = math.pi / 648000.0
    h2r    = math.pi / 12.0


    #Convert to radians
    rarad1 = ra1 * d2r
    rarad2 = ra2 * d2r
    dcrad1 = dc1 * d2r
    dcrad2 = dc2 * d2r
     
     
    deldec2 = (dcrad2 - dcrad1) / 2.0
    delra2 =  (rarad2 - rarad1) / 2.0
     
    #Haversine formula
    sindis = math.sqrt( math.sin(deldec2) * math.sin(deldec2) + math.cos(dcrad1) * math.cos(dcrad2) * math.sin(delra2)*math.sin(delra2) )
    dis = 2.0 * math.asin(sindis)
     
    #Convert to arcseconds
    disArcsec = dis / as2r

    # convert to decimal degrees
    distanceDecimalDegrees = disArcsec/3600.

    return distanceDecimalDegrees
