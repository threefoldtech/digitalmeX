import json
import datetime
import time
from zipfile import ZipFile, ZIP_DEFLATED
import uuid
import tarfile
from io import BytesIO
import mimetypes

import filetype

from bottle import request, response, Bottle, abort, static_file, template

from Jumpscale import j


class App(object):
    def __init__(self, root):
        self.root = root
        self.app = Bottle()
        self.db = j.sal.bcdbfs

        # Valid token until thousand of years
        # Generated from jwt.iousing
        # {
        #     "user": {
        #         "id": 1,
        #         "locale": "en",
        #         "viewMode": "mosaic",
        #         "perm": {
        #             "admin": true,
        #             "execute": true,
        #             "create": true,
        #             "rename": true,
        #             "modify": true,
        #             "delete": true,
        #             "share": false,
        #             "download": true
        #         },
        #         "commands": [],
        #         "lockPassword": false
        #     },
        #     "exp": 156691277633,
        #     "iat": 1566905576,
        #     "iss": "File Browser"
        # }
        self.TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7ImlkIjoxLCJsb2NhbGUiOiJlbiIsInZpZXdNb2RlIjoibW9zYWljIiwicGVybSI6eyJhZG1pbiI6dHJ1ZSwiZXhlY3V0ZSI6dHJ1ZSwiY3JlYXRlIjp0cnVlLCJyZW5hbWUiOnRydWUsIm1vZGlmeSI6dHJ1ZSwiZGVsZXRlIjp0cnVlLCJzaGFyZSI6ZmFsc2UsImRvd25sb2FkIjp0cnVlfSwiY29tbWFuZHMiOltdLCJsb2NrUGFzc3dvcmQiOmZhbHNlfSwiZXhwIjoxNTY2OTEyNzc2MzMsImlhdCI6MTU2NjkwNTU3NiwiaXNzIjoiRmlsZSBCcm93c2VyIn0.GaBiL_MeqDev0695MRqE3RhmGatouIT4BtlvpTI4P1A'

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
            response.set_header('Content-Type', 'text/plain; charset=utf-8')
            return '200 OK'

        @self.app.route('/api/resources/<dir:path>/', method='delete')
        def delete_dir(dir):
            dir = j.sal.fs.joinPaths('/', dir).rstrip('/')
            if j.sal.bcdbfs.dir_exists(dir):
                self.db.dir_remove(dir)

                response.set_header('Content-Type', 'text/plain; charset=utf-8')
                response.set_header('X-Content-Type-Options', 'nosniff')
                response.set_header('X-Renew-Token', 'true')
                return '200 OK'

            response.set_header('X-Content-Type-Options', 'nosniff')
            response.set_header('X-Renew-Token', 'true')
            response.set_header('Content-Type', 'text/plain; charset=utf-8')
            return '409 Conflict'

        @self.app.route('/api/resources/<path:re:.*>', method='post')
        def upload_file(path):
            file = j.sal.fs.joinPaths('/', path)
            override = request.GET.get('override') == 'true'

            def create(file):
                content_type = 'text/plain'
                if request.body.seek(0,2) == 0:
                    self.db.file_create_empty(file)
                else:
                    request.body.seek(0)
                    buff = request.body.read(1024)
                    request.body.seek(0)
                    mtype = filetype.guess(buff)

                    if mtype:
                        content_type = mtype.mime
                    else:
                        x = mimetypes.MimeTypes()
                        types = {}
                        for l in x.types_map:
                            types.update(l)
                        ct = types.get('.' + j.sal.fs.getFileExtension(file))
                        if ct:
                            content_type = ct
                    self.db.file_write(file, request.body, append=True, create=True)

                obj = self.db._file_model.get_by_name(name=file)[0]
                obj.content_type = content_type
                obj.epoch = int(time.time())
                obj.save()

            if not j.sal.bcdbfs.file_exists(file):
                create(file)
            elif j.sal.bcdbfs.file_exists(file) and override:
                create(file)
            else:
                response.set_header('X-Content-Type-Options', 'nosniff')
                response.set_header('X-Renew-Token', 'true')
                response.set_header('Content-Type', 'text/plain; charset=utf-8')
                return '409 Conflict'

            response.set_header('X-Content-Type-Options', 'nosniff')
            response.set_header('X-Renew-Token', 'true')
            response.set_header('Etag', '15bed3cb4c34f4360')
            response.set_header('Content-Type', 'text/plain; charset=utf-8')
            return '200 OK'

        @self.app.route('/api/resources/<path:re:.*>', method='put')
        def create_file(path):
            def create(file):
                buff = request.body.read(1024)
                request.body.seek(0)
                content_type = 'text/plain'
                mtype = filetype.guess(buff)
                if mtype:
                    content_type = mtype.mime
                else:
                    x = mimetypes.MimeTypes()
                    types = {}
                    for l in x.types_map:
                        types.update(l)
                    ct = types.get('.' + j.sal.fs.getFileExtension(file))
                    if ct:
                        content_type = ct
                self.db.file_write(file, request.body, append=True, create=True)
                obj = self.db._file_model.get_by_name(name=file)[0]
                obj.content_type = content_type
                obj.epoch = int(time.time())
                obj.save()

            file = j.sal.fs.joinPaths('/', path)
            override = request.GET.get('override') == 'true'
            obj = self.db._file_model.get_by_name(name=file)[0]

            if obj.size_bytes == 0:
                override = True

            if j.sal.bcdbfs.file_exists(file) and override:
                self.db.file_delete(file)
                create(file)
            elif not j.sal.bcdbfs.file_exists(file):
                create(file)
            else:
                response.set_header('X-Content-Type-Options', 'nosniff')
                response.set_header('X-Renew-Token', 'true')
                response.set_header('Content-Type', 'text/plain; charset=utf-8')
                return '409 Conflict'

            response.set_header('X-Content-Type-Options', 'nosniff')
            response.set_header('X-Renew-Token', 'true')
            response.set_header('Etag', '15bed3cb4c34f4360')
            response.set_header('Content-Type', 'text/plain; charset=utf-8')
            return '200 OK'

        @self.app.route('/api/resources/<path:re:.*>', method='delete')
        def delete_file(path):
            file = j.sal.fs.joinPaths('/', path)

            if j.sal.bcdbfs.file_exists(file):
                self.db.file_delete(file)

                response.set_header('X-Content-Type-Options', 'nosniff')
                response.set_header('X-Renew-Token', 'true')
                response.set_header('Etag', '15bed3cb4c34f4360')
                response.set_header('Content-Type', 'text/plain; charset=utf-8')
                return '200 OK'

            response.set_header('X-Content-Type-Options', 'nosniff')
            response.set_header('X-Renew-Token', 'true')
            response.set_header('Content-Type', 'text/plain; charset=utf-8')
            return '409 Conflict'

        @self.app.route('/api/resources/<dir:path>/', method='patch')
        def dir_copy_rename_move(dir):
            src = j.sal.fs.joinPaths('/', dir)
            action = request.GET.get('action')
            destination = request.GET.get('destination')

            def copy_dir(src, dest):
                self.db.dir_copy(src, dest)

            def move_dir(src, dest):
                self.db.dir_copy(src, dest)
                self.db.dir_remove(src)

            if action == 'copy':
                copy_dir(src, destination)
            if action in ['move', 'rename']:
                move_dir(src, destination)

            response.set_header('Content-Type', 'text/plain; charset=utf-8')
            response.set_header('X-Content-Type-Options', 'nosniff')
            response.set_header('X-Renew-Token', 'true')
            return '200 OK'

        @self.app.route('/api/resources/<path:re:.*>', method='patch')
        def file_copy_rename_move(path):
            file = j.sal.fs.joinPaths('/', path)
            action = request.GET.get('action')
            destination = request.GET.get('destination')

            def copy_file(src, dest):
                self.db.file_copy(src, dest)

            def move_file(src, dest):
                self.db.file_copy(src, dest)
                self.db.file_delete(src)

            if action == 'copy':
                copy_file(file, destination)
            if action in ['move', 'rename']:
                move_file(file, destination)

            response.set_header('Content-Type', 'text/plain; charset=utf-8')
            response.set_header('X-Content-Type-Options', 'nosniff')
            response.set_header('X-Renew-Token', 'true')
            return '200 OK'

        @self.app.route('/api/resources/<path:re:.*>', method='get', name='list')
        def resources(path=''):

            def get_type(content_type):
                if 'text' in content_type:
                    return 'text'
                if 'image' in content_type:
                    return 'image'

                if 'video' in content_type:
                    return 'video'

                return 'blob'

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
                dirs = self.db.list_dirs(path)
                files = self.db.list_files(path)
                for file in files:
                    path_ = j.sal.fs.joinPaths(path, file)
                    obj = self.db._file_model.get_by_name(name=path_)[0]
                    item = {'path': path_, 'name':j.sal.fs.getBaseName(file), 'size':obj.size_bytes, 'extension': '.{}'.format(j.sal.fs.getFileExtension(path)).rstrip('.'), 'modified': datetime.datetime.fromtimestamp(obj.epoch).strftime("%Y-%m-%dT%H:%M:%S.%f%Z"), 'mode':420, "isDir": False, 'type': get_type(obj.content_type)}
                    items.append(item)

                for dir in dirs:
                    path_ = j.sal.fs.joinPaths(path, dir)
                    obj = self.db._dir_model.get_by_name(name=path_)[0]
                    item = {'path': path_, 'name': j.sal.fs.getBaseName(dir), 'size': 4096, 'extension': '', 'modified': datetime.datetime.fromtimestamp(obj.epoch).strftime("%Y-%m-%dT%H:%M:%S.%f%Z"), 'mode': 2147484141, "isDir": True, 'type': ''}
                    items.append(item)

                response.set_header('X-Renew-Token', 'true')
                parent_obj = self.db._dir_model.get_by_name(name=path)[0]
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
            return json.dumps(
                {'content': content,
                 'checksums': {'md5': "N/A", 'sha1': "N/A",'sha256': "N/A",'sha512': "N/A",},
                 'path': path,
                 'name': j.sal.fs.getBaseName(path),
                 'size': size,
                 'extension': '.{}'.format(j.sal.fs.getFileExtension(path)).rstrip('.'),
                 'modified': modified,
                 'mode': 420,
                 "isDir": False,
                 'type': get_type(obj.content_type)
                 })

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
                      "share": False,
                      "download": True
                      },
                 "commands": [],
                 "sorting": {"by": "name", "asc": False},
                 "rules": []
                 }
            ])

        @self.app.route('/api/raw/<file:path>')
        def download_single(file):
            """
            single file or single dir
            """
            path = j.sal.fs.joinPaths('/', file)
            if path.endswith('/'):  # download_dir (this is a multi file downlad)
                # locate download_many action and call it
                route = [r for r in self.app.routes if r.name=='download_many'][0]
                return route.call(files=path)
            # download single file
            inline = request.GET.get('inline') == 'true'
            obj = self.db._file_model.get_by_name(name=path)[0]

            response.set_header('X-Renew-Token', 'true')
            response.set_header('Content-Type', obj.content_type)

            if inline:
                response.set_header('Content-Disposition', 'inline')
                response.set_header('Accept-Ranges', 'bytes')
            else:
                response.set_header('Content-Disposition', 'attachment; filename*=utf-8''%s' % j.sal.fs.getBaseName(file))
            return self.db.file_read(path)

        @self.app.route('/api/raw/', name='download_many')
        def download_many(files=None):
            """
            full directory (recursive) or many files
            """
            def list_files_recursively(dir):
                dir = dir.rstrip('/')
                res = self.db.list_files(dir)
                for d in self.db.list_dirs(dir):
                    res.extend(list_files_recursively(d))
                return res

            def zip(files, archive_name):
                with ZipFile('/tmp/%s' % archive_name, 'w', ZIP_DEFLATED) as z:
                    for file in files:
                        c = self.db.file_read(file)
                        z.writestr(file, c)

            def tar(files, archive_name, mode=''):
                tar = tarfile.open('/tmp/%s' % archive_name, 'w:%s' % mode)
                for file in files:
                    c = self.db.file_read(file)
                    file_obj = BytesIO(c)
                    info = tarfile.TarInfo(name=file)
                    info.size = len(c)
                    tar.addfile(tarinfo=info, fileobj=file_obj)
                tar.close()

            files = files or request.GET.get('files')
            requested_files = files.split(',')

            algorithm = request.GET.get('algo')
            files = []

            for file in requested_files:
                if self.db.is_file(file):
                    files.append(file)
                else:
                    files.extend(list_files_recursively(file))

            name = str(uuid.uuid4())

            content_type = 'application/octet-stream'

            if algorithm == 'zip':
                file_name = 'filemanager.zip'
                content_type = 'application/zip'
                response.set_header('Transfer-Encoding', 'chunked')
                zip(files, name)
            elif algorithm == 'tar':
                file_name = 'filemanager.tar'
                tar(files, name, mode='')
            elif algorithm == 'targz':
                file_name = 'filemanager.tar.gz'
                tar(files, name, mode='gz')
            elif algorithm == 'tarbz2':
                file_name = 'filemanager.tar.bz2'
                tar(files, name, mode='bz2')
            elif algorithm == 'tarxz':
                file_name = 'filemanager.tar.xz'
                tar(files, name, mode='xz')

            response.set_header('Content-Disposition', "attachment; filename*=utf-8''%s" % file_name)
            response.set_header('X-Renew-Token', 'true')
            response.set_header('Content-Type', content_type)

            return open('/tmp/%s' % name, 'rb')

        @self.app.route('/')
        def home():
            return static_file('index.html', root="%s/static" % self.root)

        @self.app.route('/files/')
        def home():
            return static_file('index.html', root="%s/static" % self.root)

        @self.app.route('/files')
        def home2():
            return static_file('index.html', root="%s/static" % self.root)

        @self.app.route('/files/<path:path>')
        def home3(path):
            return static_file('index.html', root="%s/static" % self.root)

    def __call__(self):
        return self.app

