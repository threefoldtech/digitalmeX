

# Copyright (C) 2019 :  TF TECH NV in Belgium see https://www.threefold.tech/
# This file is part of jumpscale at <https://github.com/threefoldtech>.
# jumpscale is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# jumpscale is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License v3 for more details.
#
# You should have received a copy of the GNU General Public License
# along with jumpscale or jumpscale derived works.  If not, see <http://www.gnu.org/licenses/>.


from Jumpscale import j

STATIC_DIR = "/sandbox/var/gdrive/static"


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
        172.17.0.2:8080/gdrive/slide/1-Eh4ghLxoVCGSt5onNb8Dx9sCi3-OJ3mNQGo0h9CUgg/second
        """

        doctypes_map = {"doc": "drive", "sheet": "drive", "slide": "slides"}
        cl = j.clients.gdrive.main

        if not doctype in doctypes_map:
            raise RuntimeError("invalid type")

        service_name = doctypes_map[doctype]
        if doctype in ["doc", "sheet"]:

            path = j.sal.fs.joinPaths(STATIC_DIR, doctype, "{}.pdf".format(guid1))
            cl.exportFile(guid1, destpath=path, service_name=service_name, service_version="v3")

            out = schema_out.new()
            out.res = "/gdrive_static/{}/{}.pdf".format(doctype, guid1)
            return out

        elif doctype == "slide":
            path = j.sal.fs.joinPaths(STATIC_DIR, doctype)
            cl.exportSlides(guid1, path)
            out = schema_out.new()
            if j.sal.fs.exists("{}/{}/{}.png".format(path, guid1, guid2), followlinks=True):
                out.res = "/gdrive_static/slide/{}/{}.png".format(guid1, guid2)
            else:
                meta = cl.get_presentation_meta("{}/presentations.meta.json".format(path), guid1)
                guid2 = meta[guid2]
                guid2 = guid2.split("_", maxsplit=1)[1]  # remove the 0x_ part from the file name
                out.res = "/gdrive_static/slide/{}/{}".format(guid1, guid2)
            return out
