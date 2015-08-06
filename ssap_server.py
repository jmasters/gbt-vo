import web
from gcirc import gcirc
import math

db = web.database(dbn='sqlite', db='gbt_spectra.sqlite')
def get_spectra(params):
    wherestring = ''
    print 'params', params

    # if the "band" parameter is present
    if hasattr(params, 'band'):

        # if there is a range
        if '/' in params.band:
            wavelen_smaller, wavelen_bigger = params.band.split('/')

            freq_lo = None
            freq_hi = None

            # convert meters to GHz
            if wavelen_bigger:
                freq_lo = .3/float(wavelen_bigger)

            if wavelen_smaller:
                freq_hi = .3/float(wavelen_smaller)

            # case of closed search range 'band_lo/band_hi'
            if freq_lo and freq_hi:
                wherestring += ' restfreq_ghz >= \'{0}\' and restfreq_ghz <= \'{1}\''.format(str(freq_lo), str(freq_hi))
            # case of open search range '/band_hi'
            elif (not freq_lo) and freq_hi:
                wherestring += ' restfreq_ghz <= \'{0}\''.format(str(freq_hi))
            # case of open search range 'band_lo/'
            elif freq_lo and (not freq_hi):
                wherestring += ' restfreq_ghz >= \'{0}\''.format(str(freq_lo))
            # case of open search range on both ends '/'
            else:
                wherestring = ''

        else:
            wherestring += ' restfreq_ghz = \'{0}\''.format(str(params.band))

    # if the 'format' paramter is present
    if hasattr(params, 'format'):
        if (params.format.lower() != 'native') or  (params.format.lower() != 'all'):
            raise

    # if the 'request' paramter is present
    if hasattr(params, 'request'):
        if (params.request.lower() != 'querydata'):
            raise

    # if the time paramter is present
    if hasattr(params, 'time'):
        if '/' in params.time:
            time_lo, time_hi = params.time.split('/')

            if (time_lo or time_hi) and wherestring:
                wherestring += ' and'

            if time_lo and time_hi:
                wherestring += ' timestamp >= \'{0}\' and timestamp <= \'{1}\''.format(time_lo, time_hi)
            elif (not time_lo) and time_hi:
                wherestring += ' timestamp <= \'{0}\''.format(time_hi)
            elif time_lo and (not time_hi):
                wherestring += ' timestamp >= \'{0}\''.format(time_lo)

        else:
            wherestring += ' timestamp like \'{0}%\''.format(params.time)

    print 'wherestring', wherestring

    if wherestring:
        spectra = [x for x in db.select('spectra', where=wherestring)]
    else:
        spectra = [x for x in db.select('spectra')]

    print 'rows returned from db query: {0}'.format(len(spectra))

    return spectra

render = web.template.render('templates/', cache=False)
urls = ('/', 'SSAPsearch')
app = web.application(urls, globals())

class SSAPsearch:
    def GET(self):
        try:
            i = web.input()

            # make all parameters lowercase
            for kk in i.keys():
                i[kk.lower()] = i.pop(kk)

            print i

            keys = i.keys()
            if not(('time' in keys) or
                   ('band' in keys) or
                   (('pos' in keys) and ('size' in keys))):
                print 'ERROR: missing time or band or pos/size'
                raise

            spectra = get_spectra(i)
            for spec in spectra:
                spec['beamsize'] = ((1.22*(3e8/(spec['restfreq_ghz']*1e9)))/100)*(180/math.pi)*.65

            if hasattr(i, 'pos') and hasattr(i, 'size'):
                ra, dec = i.pos.split(',')
                within_radius = []
                for spec in spectra:
                    dist = gcirc(ra, dec, spec['ra'], spec['dec'])

                    spec['dist'] = dist
                    if float(dist) <= float(i.size):
                        within_radius.append(spec)

                web.header('Content-Type', 'text/xml')
                print len(within_radius),'within search radius'
                return render.ssap_response(within_radius,"OK",i)

            else:
                return render.ssap_response(spectra,"OK",i)
        except:
#            import pdb; pdb.set_trace()
            return render.ssap_response([],"ERROR",i)
            

if __name__ == "__main__":

    app.run()

# http://mycone.org/cgi-bin/search?RA=180.567&DEC=-30.45&SR=0.0125
