import web
from gcirc import gcirc

db = web.database(dbn='sqlite', db='gbt_spectra.sqlite')
def get_spectra():
    return [x for x in db.select('spectra')]

spectra = get_spectra()

render = web.template.render('templates/', cache=False)
urls = ('/', 'Conesearch')
app = web.application(urls, globals())

class Status:
    def __init__(self, val, desc):
        self.value = val
        self.description = desc

class Conesearch:
    def GET(self):
        try:
            i = web.input()

            # make all parameters lowercase
            for kk in i.keys():
                i[kk.lower()] = i.pop(kk)

            print i

            inrad = []

            for spec in spectra:
                dist = gcirc(i.ra, i.dec, spec['ra'], spec['dec'])
                spec['dist'] = dist
                if float(dist) <= float(i.sr):
                    inrad.append(spec)

            web.header('Content-Type', 'text/xml')

            status = Status("OK", "")
            return render.cone_search_response(inrad, status)
        except:
            status = Status("ERROR", "Something went wrong")
            return render.cone_search_response([], status)
            

if __name__ == "__main__":

    app.run()

# http://mycone.org/cgi-bin/search?RA=180.567&DEC=-30.45&SR=0.0125
