from Jumpscale import j

STATIC_DIR = '/sandbox/var/gdrive/static'

"""
mkdir -p /sandbox/var/gdrive/static
mkdir /sandbox/var/gdrive/static/doc
mkdir /sandbox/var/gdrive/static/slide

ln -s /sandbox/code/github/threefoldfoundation/lapis-wiki/static/gdrive /sandbox/var/gdrive/static/
"""

class gdrive(j.application.JSBaseClass):

    def file_get(self, doctype, guid1, guid2, schema_out):
        """
        ```in
        doctype = "" (S)
        guid1 = (S)
        guid2 = "" (S)
        ```
        ```out
        res = (S)
        ```
        :param collection:
        :param bucket:
        :param text:
        :return:
        """

        doctypes_map = {
            'doc': 'drive',
            'slide': 'slides',
        }
        cl = j.clients.gdrive.main

        if not doctype in doctypes_map:
            raise RuntimeError("invalid type")

        service_name = doctypes_map[doctype]
        if doctype == "doc":

            path = j.sal.fs.joinPaths(STATIC_DIR, doctype, "{}.pdf".format(guid1))
            cl.exportFile(guid1, destpath=path, service_name=service_name, service_version="v3")

            out = schema_out.new()
            out.res = "/static/gdrive/doc/{}.pdf".format(guid1)
            return out

        elif doctype == "slide":
            cl.exportSlides(guid1, j.sal.fs.joinPaths(STATIC_DIR, doctype))
            out = schema_out.new()
            if not guid2:
                raise NotImplemented()
            out.res = "/static/gdrive/slide/{}/{}.png".format(guid1, guid2)
            return out
