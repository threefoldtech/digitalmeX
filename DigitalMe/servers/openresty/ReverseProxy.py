from Jumpscale import j

JSConfigs = j.application.JSBaseConfigsClass


class ReverseProxy(j.application.JSBaseConfigClass):
    """
    Reverse Proxy using openresty server
    """

    _SCHEMATEXT = """
        @url = jumpscale.openresty.reverseproxy.1
        name* = (S)
        port_source = 80
        ipaddr_dest = "127.0.0.1"
        port_dest = 80
        location = 
        domain = ""
        
        """

    CONFIG = """
        server {
            listen {{obj.port_source}};
            listen [::]:{{obj.port_source}};
            
            {% if obj.domain %}
            server_name ~^(www\.)?{{domain}}$;
            {% endif %}
            
            location /{{obj.location}} {
              proxy_pass http://{{obj.ipaddr_dest}}:{{obj.port_dest}}/;
            }
        }
        """

    def configure(self):
        """

        when initializing this class it will already write the config, but this method can be called to rewrite it

        """
        r = j.tools.jinja2.template_render(text=self.CONFIG, obj=self)
        j.sal.fs.writeFile("%s/servers/proxy_%s.conf" % (j.servers.openresty._web_path, self.name), r)


class ReverseProxies(j.application.JSBaseConfigsClass):

    _CHILDCLASS = ReverseProxy
