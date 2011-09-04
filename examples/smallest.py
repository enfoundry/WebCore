import web.core
 
class RootController(web.core.Controller):
    def index(self, name="program"):
        return 'Hello, {name}.'.format(name=name)
 
app = web.core.Application.factory(root=RootController, debug=False)
__import__('paste.httpserver').httpserver.serve(app, host='127.0.0.1', port='8080')