import inspect

from Jumpscale import j

from .GedisCmd import GedisCmd

JSBASE = j.application.JSBaseClass

SCHEMA = """
@url = jumpscale.gedis.api
namespace = ""
name = ""
cmds = (LO) !jumpscale.gedis.cmd
schemas = (LO) !jumpscale.gedis.schema

@url = jumpscale.gedis.cmd
name = ""
comment = ""
schema_in = ""
schema_out = ""
args = (ls)

@url = jumpscale.gedis.schema
url = ""
content = ""
"""


class GedisCmds(JSBASE):
    """
    cmds understood by gedis server
    """

    def __init__(self, server=None, namespace="default", name="", path="", capnpbin=None):
        JSBASE.__init__(self)

        if path is "" and capnpbin is None:
            raise RuntimeError("path cannot be None")

        self.path = path
        self.server = server

        self.schema = j.data.schema.get(SCHEMA)
        # self.schema = j.data.schema.get(url="jumpscale.gedis.api")

        self._cmds = {}

        if capnpbin:
            self.data = self.schema.get(capnpbin=capnpbin)
        else:
            cname = j.sal.fs.getBaseName(path)[:-3]
            klass = j.tools.codeloader.load(obj_key=cname, path=path, reload=False)
            kobj = klass()  # this is the actor obj

            key = "%s__%s" % (namespace, cname.replace(".", "_"))

            self.server.actors[key] = kobj  # as used in gedis server (when serving the commands)

            self.data = self.schema.new()
            self.data.name = name
            self.data.namespace = namespace

            for member_name, item in inspect.getmembers(klass):
                if member_name.startswith("_"):
                    continue
                if member_name.startswith("logger"):
                    continue
                if member_name in ["cache"]:
                    continue
                if inspect.isfunction(item):
                    cmd = self.data.cmds.new()
                    cmd.name = member_name
                    code = inspect.getsource(item)
                    self._method_source_process(cmd, code)

    @property
    def name(self):
        return self.data.name

    @property
    def namespace(self):
        return self.data.namespace

    @property
    def cmds(self):
        if self._cmds == {}:
            self._log_debug('Populating commands for namespace(%s)', self.data.name)
            for s in self.data.schemas:
                if not s.url in j.data.schema.schemas:
                    j.data.schema.get(s.content, url=s.url)
            for cmd in self.data.cmds:
                self._log_debug("\tpopulate: %s", cmd.name)
                self._cmds[cmd.name] = GedisCmd(self.namespace, cmd)
        return self._cmds

    def cmd_exists(self, name):
        return name in self._cmds

    def __repr__(self):
        return 'CMDS:%s' % (self.namespace)

    __str__ = __repr__

    def _method_source_process(self, cmd, txt):
        """
        return code, comment, schema_in, schema_out, args
        """
        txt = j.core.text.strip(txt)
        code = ""
        comment = ""
        schema_in = ""
        schema_out = ""
        args = []

        state = "START"

        for line in txt.split("\n"):
            lstrip = line.strip().lower()
            if state == "START" and lstrip.startswith("def"):
                state = "DEF"
                if "self" in lstrip:
                    if "," in lstrip:
                        _, arg = lstrip.split(",", 1)
                        args = arg[:arg.index(')')]
                        args = [j.core.text.strip(x) for x in args.split(',')]
                    else:
                        args = []
                else:
                    _, arg = lstrip.split("(", 1)
                    args = arg.split(")", 1)
                continue
            if lstrip.startswith("\"\"\""):
                if state == "DEF":
                    state = "COMMENT"
                    continue
                if state == "COMMENT":
                    state = "CODE"
                    continue
                raise RuntimeError()
            if lstrip.startswith("```") or lstrip.startswith("'''"):
                if state.startswith("SCHEMA"):  # are already in schema go back to comment
                    state = "COMMENT"
                    continue
                if state == "COMMENT":  # are in comment, now found the schema
                    if lstrip.endswith("out"):
                        state = "SCHEMAO"
                    else:
                        state = "SCHEMAI"
                    continue
                raise RuntimeError()
            if state == "SCHEMAI":
                schema_in += "%s\n" % line
                continue
            if state == "SCHEMAO":
                schema_out += "%s\n" % line
                continue
            if state == "COMMENT":
                comment += "%s\n" % line
                continue
            if state == "CODE" or state == "DEF":
                code += "%s\n" % line
                continue
            raise RuntimeError()

        # cmd.code = j.core.text.strip(code)
        cmd.comment = j.core.text.strip(comment)
        cmd.schema_in = self._schema_process(cmd, schema_in)
        cmd.schema_out = self._schema_process(cmd, schema_in)
        if "schema_out" in args:
            args.pop(args.index("schema_out"))
        cmd.args = args
        return cmd

    def _schema_get(self, url):
        url = url.lower().strip("!").strip()
        for s in self.data.schemas:
            if s.url == url:
                return s.url, s.content
        return None, None

    def _schema_url_add(self, url, content):
        """
        see if url is already in data object if yes then add it
        :param url:
        :param content:
        :return:
        """
        url = url.strip()
        if "#" in url:
            url = url.split("#", 1)[0].strip()
        if "!" in url:
            raise RuntimeError("cannot have ! in url")
        url2, content2 = self._schema_get(url)
        if not url2:
            # means we did not find it yet
            s = self.data.schemas.new()
            s.url = url
            s.content = content

    def _schema_process(self, cmd, txt):
        txt = j.core.tools.text_strip(txt)
        if txt.strip() == "":
            return ""
        url = ""
        for line in txt.split("\n"):
            line_strip = line.strip()
            if line_strip == "":
                continue
            if line_strip.startswith("!"):
                if url is not "":
                    raise RuntimeError("cannot only be 1")
                url = line_strip.strip("!")
            elif line_strip.find("!") != -1:
                url2 = line_strip.split("!", 1)[1]
                s2 = j.data.schema.get(url=url2)
                self._schema_url_add(url2, s2.text)
            if url == "":
                md5 = j.data.hash.md5_string(txt.strip())
                url = "actors.%s.%s.%s.%s" % (self.data.namespace, self.data.name, cmd.name, md5)

            if url not in j.data.schema.schemas:
                j.data.schema.get(txt, url=url)  # will add the schema with right url
            self._schema_url_add(url, txt)
            return url
