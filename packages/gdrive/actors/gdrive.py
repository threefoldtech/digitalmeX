from Jumpscale import j

STATIC_DIR = '/sandbox/var/


class gdrive(j.application.JSBaseClass):

    def file_get(self, doctype, guid1, guid2, schema_out):
        """
        ```in
        doctype = "" (S)
        guid1 = (S)
        guid2 = "" (S)
        ```
        ```out
        res = (LS)
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
        #
        # http: // $IPADDR / gdrive / slide /$gslide_slide_guid.png
        # http: // $IPADDR / gdrive / slide /$gpresentation_guid /$slidename.png (LATER)
        # http: // $IPADDR / gdrive / doc /$gdoc_guid.pdf (NOW)
        # http: // $IPADDR / gdrive / spreadsheet /$sheet_guid.png(pickup LATER
        # a
        # suitable
        # alternative
        # for pngs)
        # http: // $IPADDR / gdrive / doc /$gdoc_guid.md

        cl = j.clients.gdrive.main

        # TODO: FIX CHECKS
        assert doctype in doctypes_map
        service_name = doctypes_map[doctype]
        if doctype == "doc":
            gfile = cl.getFile(guid1, service_name=service_name, service_version="v3")
            gfile.exportPDF(self, path=j.sal.fs.joinPaths(STATIC_DIR, "gdrive", doctype, "{guid}.pdf".format(guid1)))
        elif doctype == "slide":
            cl.exportSlides(guid1, "/tmp/exportedslides/")
            # rename all the slides in exportedslides/$prsentation_name/



