import web

urls = (
  '/submit', 'Index'
)


app = web.application(urls, globals())

render = web.template.render('templates/')

class Index(object):
    def GET(self):
        form = web.input(search="")
        text = "You searched for %s" % form.search

        return text

if __name__ == "__main__":
    app.run()