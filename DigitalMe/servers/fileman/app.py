import json
import datetime
import time

from bottle import request, response, Bottle, abort, static_file, template

from Jumpscale import j


class App(object):
    def __init__(self, root):
        self.root = root
        self.app = Bottle()
        self.db = j.sal.bcdbfs

        # Valid token until thousand of years
        self.TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7ImlkIjoxLCJsb2NhbGUiOiJlbiIsInZpZXdNb2RlIjoibW9zYWljIiwicGVybSI6eyJhZG1pbiI6dHJ1ZSwiZXhlY3V0ZSI6dHJ1ZSwiY3JlYXRlIjp0cnVlLCJyZW5hbWUiOnRydWUsIm1vZGlmeSI6dHJ1ZSwiZGVsZXRlIjp0cnVlLCJzaGFyZSI6dHJ1ZSwiZG93bmxvYWQiOnRydWV9LCJjb21tYW5kcyI6W10sImxvY2tQYXNzd29yZCI6ZmFsc2V9LCJleHAiOjE1NjY5MTI3NzYzMywiaWF0IjoxNTY2OTA1NTc2LCJpc3MiOiJGaWxlIEJyb3dzZXIifQ.-rYOxPYN3DNjRbMbgzw5pEx_hagMnmJQP8qHw519P3M'

        @self.app.route('/api/login', method='post')
        def login():
            response.set_header('Content-Type', 'cty')
            return self.TOKEN

        @self.app.route('/api/renew', method='post')
        def renew():
            response.set_header('X-Renew-Token', 'true')
            response.set_header('Content-Type', 'cty')
            return self.TOKEN

        @self.app.route("/static/<path:path>")
        def static(path):
            return static_file(path, root="%s/static" % self.root)

        @self.app.route('/api/resources/<dir:path>/', method='post')
        def create_dir(dir):
            dir = j.sal.fs.joinPaths('/', dir).rstrip('/')
            override = request.GET.get('override') == 'true'
            if not j.sal.bcdbfs.dir_exists(dir):
                self.db.dir_create(dir)
            elif j.sal.bcdbfs.dir_exists(dir) and override:
                self.db.dir_create(dir)

            obj = self.db._dir_model.get_by_name(name=dir)[0]
            obj.epoch = int(time.time())
            obj.save()

            response.set_header('X-Content-Type-Options', 'nosniff')
            response.set_header('X-Renew-Token', 'true')
            return '200 OK'

        @self.app.route('/api/resources/<path:re:.*>', method='post')
        def create_empty_file(path):
            file = j.sal.fs.joinPaths('/', path)
            override = request.GET.get('override') == 'true'

            if not j.sal.bcdbfs.file_exists(file):
                self.db.file_create_empty(file)
            elif j.sal.bcdbfs.dir_exists(file) and override:
                self.db.file_create_empty(file)
            else:
                response.set_header('X-Content-Type-Options', 'nosniff')
                response.set_header('X-Renew-Token', 'true')
                response.set_header('Content-Type', 'text/plain; charset=utf-8')
                return '409 Conflict'

            obj = self.db._file_model.get_by_name(name=file)[0]
            obj.epoch = int(time.time())
            obj.save()

            response.set_header('X-Content-Type-Options', 'nosniff')
            response.set_header('X-Renew-Token', 'true')
            response.set_header('Etag', '15bed3cb4c34f4360')
            response.set_header('Content-Type', 'text/plain; charset=utf-8')
            return '200 OK'

        @self.app.route('/api/resources/<path:re:.*>', method='put')
        def create_file(path):
            file = j.sal.fs.joinPaths('/', path)
            override = request.GET.get('override') == 'true'
            obj = self.db._file_model.get_by_name(name=file)[0]

            if obj.size_bytes == 0:
                override = True

            if j.sal.bcdbfs.file_exists(file) and override:
                self.db.file_delete(file)
                for line in request.body:
                    self.db.file_write(file, line.decode(), append=True, create=True)
            elif not j.sal.bcdbfs.dir_exists(file):
                for line in request.body:
                    self.db.file_write(file, line.decode(), append=True, create=True)
            else:
                response.set_header('X-Content-Type-Options', 'nosniff')
                response.set_header('X-Renew-Token', 'true')
                response.set_header('Content-Type', 'text/plain; charset=utf-8')
                return '409 Conflict'

            obj = self.db._file_model.get_by_name(name=file)[0]
            obj.epoch = int(time.time())
            obj.save()

            response.set_header('X-Content-Type-Options', 'nosniff')
            response.set_header('X-Renew-Token', 'true')
            response.set_header('Etag', '15bed3cb4c34f4360')
            response.set_header('Content-Type', 'text/plain; charset=utf-8')
            return '200 OK'

        @self.app.route('/api/resources/<path:re:.*>', method='get')
        def resources(path=''):
            list = True

            if not path:
                path = '/' # root

            if not path.endswith('/'):
                list = False

            path = j.sal.fs.joinPaths('/', path).rstrip('/') or '/'

            response.set_header('X-Renew-Token', 'true')
            response.set_header('Content-Type', 'application/json; charset=utf-8')
            items = []
            if list:
                parent_obj = self.db._dir_model.get_by_name(name=path)[0]
                dirs = self.db.list_dirs(path)
                files = self.db.list_files(path)

                for file in files:
                    path_ = j.sal.fs.joinPaths(path, file)
                    obj = self.db._file_model.get_by_name(name=path_)[0]
                    item = {'path': path_, 'name':j.sal.fs.getBaseName(file), 'size':obj.size_bytes, 'extension': '.{}'.format(j.sal.fs.getFileExtension(path)).rstrip('.'), 'modified': datetime.datetime.fromtimestamp(obj.epoch).strftime("%Y-%m-%dT%H:%M:%S.%f%Z"), 'mode':420, "isDir": False, 'type': 'text'}
                    items.append(item)

                for dir in dirs:
                    path_ = j.sal.fs.joinPaths(path, dir)
                    obj = self.db._dir_model.get_by_name(name=path_)[0]
                    item = {'path': path_, 'name': j.sal.fs.getBaseName(dir), 'size': 4096, 'extension': '', 'modified': datetime.datetime.fromtimestamp(obj.epoch).strftime("%Y-%m-%dT%H:%M:%S.%f%Z"), 'mode': 2147484141, "isDir": True, 'type': ''}
                    items.append(item)

                response.set_header('X-Renew-Token', 'true')
                return json.dumps(
                    {"items": items,
                     "numDirs": len(dirs),
                     "numFiles": len(files),
                     "sorting": {"by": "name", "asc": False},
                     "path": path,
                     "name": "filemanager",
                     "size": 4096,
                     "extension": "",
                     "modified": datetime.datetime.fromtimestamp(parent_obj.epoch).strftime("%Y-%m-%dT%H:%M:%S.%f%Z"),
                     "mode": 2147484141,
                     "isDir": True,
                     "type": ""
                     })

            # file info
            modified = time.time()
            size = 0
            content = ''
            if self.db.file_exists(path):
                obj = self.db._file_model.get_by_name(name=path)[0]
                modified = obj.epoch
                size = obj.size_bytes
                content = obj.content
            return json.dumps({'content': content, 'path': path, 'name': j.sal.fs.getBaseName(path), 'size': size, 'extension': '.{}'.format(j.sal.fs.getFileExtension(path)).rstrip('.'), 'modified': modified, 'mode': 420, "isDir": False, 'type': 'text'})

        @self.app.route('/api/users')
        def users():
            return json.dumps([
                {"id": 1,
                 "username": "admin",
                 "password": "",
                 "scope": ".",
                 "locale": "en",
                 "lockPassword": False,
                 "viewMode": "mosaic",
                 "perm":
                     {"admin": True,
                      "execute": True,
                      "create": True,
                      "rename": True,
                      "modify": True,
                      "delete": True,
                      "share": True,
                      "download": True
                      },
                 "commands": [],
                 "sorting": {"by": "name", "asc": False},
                 "rules": []
                 }
            ])

        @self.app.route('/')
        def home():
            return static_file('index.html', root="%s/static" % self.root)

        @self.app.route('/files/')
        def home():
            return static_file('index.html', root="%s/static" % self.root)

    def __call__(self):
        return self.app

