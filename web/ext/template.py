# encoding: utf-8


class Extension(object):
    uses = []
    needs = []
    always = False
    never = False
    provides = []
    
    def __init__(self, config):
        """Executed to configure the extension."""
        super(Extension, self).__init__()
    
    def __call__(self, app):
        """Executed to wrap the application in middleware."""
        return app
    
    def start(self):
        """Executed during application startup just after binding the server."""
        pass
    
    def stop(self):
        """Executed during application shutdown after the last request has been served."""
        pass
    
    def prepare(self, context):
        """Executed during request set-up."""
        pass
    
    def dispatch(self, context, consumed, handler):
        """Executed as dispatch descends into a tier."""
        pass
    
    def before(self, context):
        """Executed after all extension prepare methods have been called, prior to dispatch."""
        pass
    
    def after(self, context, exc=None):
        """Executed after dispatch has returned and the response populated, prior to anything being sent to the client."""
        pass
