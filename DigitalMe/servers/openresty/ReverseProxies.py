from Jumpscale import j

JSConfigs = j.application.JSBaseConfigsClass


class ReverseProxy(j.application.JSBaseConfigClass):
    """
    Website hosted in openresty
    """

    _SCHEMATEXT = """
        @url = jumpscale.openresty.website.1
        name* = (S)
        port_source = 80
        ipaddr_dest = "127.0.0.1"
        port_dest = 80
        location = 
        domain = ""
        
        """

    # TODO: put new config in for proxy
    CONFIG = """
        server {
            {% if obj.domain %}
            server_name ~^(www\.)?{{domain}}$;
            {% endif %}
            listen {{obj.port}};
            lua_code_cache on;
        
            include vhosts/static.conf.loc;
            include vhosts/websocket.conf.loc;
            include vhosts/docsites.conf.loc;
            
            location /{{obj.location}} {
                default_type text/html;
                root {{obj.path}};
            }

        }
        
        """

    def _init(self):
        self.configure()

    def configure(self):
        """

        when initializing this class it will already write the config, but this method can be called to rewrite it

        """
        r = j.tools.jinja2.template_render(text=self.CONFIG, obj=self)
        j.sal.fs.writeFile("%s/servers/proxy_%s.conf" % (j.servers.openresty._web_path, self.name), r)


class ReverseProxies(j.application.JSBaseConfigsClass):

    _CHILDCLASS = ReverseProxy
