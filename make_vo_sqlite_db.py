#import numpy as np
import fitsio
import sys
import os
import glob
import sqlite3


def _gregorian_to_julian_date(day, month, year, hour, minute, second):
    """Converts a gregorian date to julian date.

    Keyword arguments:
    day -- 2 digit day string
    month -- 2 digit month string
    year -- 4 digit year string
    hour -- 2 digit hour string
    minute -- 2 digit minute string
    second -- N digit second string

    Returns:
    a floating point value which is the julian date
    """

    dd = int(day)
    mm = int(month)
    yyyy = int(year)
    hh = float(hour)
    minute = float(minute)
    sec = float(second)

    UT = hh+minute/60+sec/3600

    if (100*yyyy+mm-190002.5)>0:
        sig = 1
    else:
        sig=-1

    JD = 367*yyyy - int(7*(yyyy+int((mm+9)/12))/4) + int(275*mm/9) + dd + 1721013.5 + UT/24 - 0.5*sig +0.5

    return JD

def dateToMjd(dateString):
    """Convert a FITS DATE string to Modified Julian Date

    Keyword arguments:
    dateString -- a FITS format date string, ie. '2009-02-10T21:09:00.08'

    Returns:
    floating point Modified Julian Date

    """

    year  = dateString[:4]
    month = dateString[5:7]
    day   = dateString[8:10]
    hour  = dateString[11:13]
    minute= dateString[14:16]
    second= dateString[17:]

    # now convert from julian day to mjd
    jd = _gregorian_to_julian_date(day, month, year, hour, minute, second)
    mjd = jd - 2400000.5
    return mjd

# from http://www.bdnyc.org/2012/10/15/decimal-deg-to-hms/
# convert decimal degrees to HMS format
def deg2hms(ra='', dec='', doRound=False):
    RA, DEC, rs, ds = '', '', '', ''
    if dec:
        if str(dec)[0] == '-':
            ds, dec = '-', abs(dec)
        else:
            ds, dec = '+', abs(dec)
    deg = int(dec)
    decM = abs(int((dec-deg)*60))
    if doRound:
        decS = int((abs((dec-deg)*60)-decM)*60)
    else:
        decS = (abs((dec-deg)*60)-decM)*60
    DEC = '{0}{1:02d}:{2:02d}:{3:02d}'.format(ds, deg, decM, decS)
  
    if ra:
        if str(ra)[0] == '-':
            rs, ra = '-', abs(ra)
        raH = int(ra/15)
        raM = int(((ra/15)-raH)*60)
        if doRound:
            raS = int(((((ra/15)-raH)*60)-raM)*60)
        else:
            raS = ((((ra/15)-raH)*60)-raM)*60
        RA = '{0}{1:02d}:{2:02d}:{3:02.1f}'.format(rs, raH, raM, raS)
  
    if ra and dec:
        return (RA, DEC)
    else:
        return RA or DEC

if __name__ == '__main__':

    tablerows = []
    for infile in glob.glob("spectra/*fits"):
        ff = fitsio.FITS(infile)
        tdata = ff[1].read()
        tablerow = {}
        tablerow[tdata['CTYPE2'][0].strip()] = tdata['CRVAL2'][0]
        tablerow[tdata['CTYPE3'][0].strip()] = tdata['CRVAL3'][0]
        tablerow['TARGET'] = tdata['OBJECT'][0].strip()
        tablerow['RESTFREQ_GHZ'] = tdata['RESTFREQ'][0]/1e9
        tablerow['TIMESTAMP'] = tdata['DATE-OBS'][0]
        tablerow['NCHAN'] = len(tdata['DATA'][0])
        tablerow['BANDWIDTH'] = tdata['BANDWID'][0]/1e6
        tablerow['FILENAME'] = infile.split('/')[-1]
        # some data was seen where the timestamp had *'s in the FITS file
        #  the rstrip below is just to get around that weird case
        tablerow['MJD'] =  dateToMjd(tablerow['TIMESTAMP'].rstrip('*'))
        tablerows.append(tablerow)

    headers = tablerows[0].keys()

    conn = sqlite3.connect('gbt_spectra.sqlite')
    c = conn.cursor()

    # create table
    c.execute("CREATE TABLE spectra (target text, restfreq_ghz real, timestamp text, ra real, dec real, filename text, nchan long, bandwidth real, mjd real)")

    # add values to the table
    for tablerow in tablerows:
        c.execute("INSERT INTO spectra VALUES (?,?,?,?,?,?,?,?,?)",
                  (tablerow['TARGET'], tablerow['RESTFREQ_GHZ'], tablerow['TIMESTAMP'],
                   tablerow['RA'], tablerow['DEC'], tablerow['FILENAME'], tablerow['NCHAN'],
                   tablerow['BANDWIDTH'], tablerow['MJD']))

    # save the changes
    conn.commit()
    
    sys.exit()
