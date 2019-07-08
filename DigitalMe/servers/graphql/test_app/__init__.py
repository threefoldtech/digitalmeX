class TestApp(object):
    def __init__(self, app):
        self.app = app
        
    @property
    def schema(self):
        from .schema import schema
        return schema

    def __call__(self, *args, **kwargs):
        @self.app.route('/posts')
        def posts():
            return 'hi'

