from Jumpscale import j
from .OpenPublish import OpenPublish

JSConfigs = j.application.JSBaseConfigsClass


class Website(j.application.JSBaseConfigClass):
    """
    Website hosted in openresty
    """

    _SCHEMATEXT = """
        @url = jumpscale.openresty.website.1
        name* = (S)
        port = 80
        location = 
        domain = ""
        path = ""
        
        """

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

    def configure(self, config=None):
        """
        if config none then will use self.CONFIG

        config is a server config file of nginx (in text format)

        e.g.

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

        can use template variables with obj...  (obj is this obj = self)


        :param config:
        :return:
        """
        if not config:
            config = self.CONFIG
        if not config and self.port == 80 and self.domain == "":
            raise ValueError("port or domain needs to be set")

        r = j.tools.jinja2.template_render(text=self.CONFIG, obj=self)
        j.sal.fs.writeFile("%s/servers/%s.conf" % (j.servers.openresty._web_path, self.name), r)


class Websites(j.application.JSBaseConfigsClass):

    _CHILDCLASS = Website
