#import numpy as np
import fitsio
import sys
import os
import glob
import sqlite3

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
        tablerow['FILENAME'] = infile.split('/')[-1]
        tablerows.append(tablerow)

    headers = tablerows[0].keys()

    conn = sqlite3.connect('gbt_spectra.sqlite')
    c = conn.cursor()

    # create table
    c.execute("CREATE TABLE spectra (target text, restfreq_ghz real, ra real, dec real, filename text)")

    # add values to the table
    for tablerow in tablerows:
        c.execute("INSERT INTO spectra VALUES (?,?,?,?,?)",
                  (tablerow['TARGET'], tablerow['RESTFREQ_GHZ'],
                   tablerow['RA'], tablerow['DEC'], tablerow['FILENAME']))

    # save the changes
    conn.commit()
    
    sys.exit()
