import web
from gcirc import gcirc

db = web.database(dbn='sqlite', db='gbt_spectra.sqlite')
def get_spectra():
    return [x for x in db.select('spectra')]

spectra = get_spectra()

render = web.template.render('templates/', cache=False)
urls = ('/', 'Conesearch')
app = web.application(urls, globals())

class Conesearch:
    def GET(self):
        try:
            i = web.input()
            print i

            inrad = []
            for spec in spectra:
                dist = gcirc(i.ra, i.dec, spec['ra'], spec['dec'])
                #print spec['target'], dist
                spec['dist'] = dist
                if float(dist) <= float(i.sr):
                    inrad.append(spec)

    #        return render.cone(i.ra, i.dec, i.sr, inrad)
            web.header('Content-Type', 'text/xml')
            return render.response(inrad)
        except:
            return render.response([])
            

if __name__ == "__main__":

    app.run()

# http://mycone.org/cgi-bin/search?RA=180.567&DEC=-30.45&SR=0.0125
