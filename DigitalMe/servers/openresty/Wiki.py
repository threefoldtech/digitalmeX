from Jumpscale import j
from .OpenPublish import OpenPublish

JSConfigs = j.application.JSBaseConfigsClass


class Wiki(j.application.JSBaseConfigClass):
    """
    Website hosted in openresty
    """

    _SCHEMATEXT = """
        @url = jumpscale.openresty.wiki.1
        name* = (S)
        port = 80
        location = 
        domain = ""
        giturl = ""
        branch = "master"
        
        """

    CONFIG = """
        server {
            {% if obj.domain %}
            server_name ~^(wiki\.)?{{domain}}$;
            {% endif %}
            listen {{obj.port}};
            lua_code_cache on;
        
            include vhosts/static.conf.loc;
            include vhosts/websocket.conf.loc;
            include vhosts/gdrive.conf.loc;
        
            location /docsites/ {
                alias /sandbox/var/docsites/;
            }
        
            location / {
                set $name '{{name}}';
                default_type text/html;
                content_by_lua_block {
                    require("lapis").serve("applications.wiki");
                }
            }
        }
        
        server {
            {% if obj.domain %}
            server_name ~^(wiki\.)?{{domain}}$;
            {% endif %}
            listen {{obj.port}};
            lua_code_cache on;
        
            include vhosts/static.conf.loc;
            include vhosts/websocket.conf.loc;
            include vhosts/gdrive.conf.loc;
        
            location /docsites/ {
                alias /sandbox/var/docsites/;
            }
        
            location / {
                set $name '{{name}}_dev';
                default_type text/html;
                content_by_lua_block {
                    require("lapis").serve("applications.wiki");
                }
            }
        }


        }
        
        """

    def _init(self, **kwargs):

        self.update(pull=False)

    def update(self, pull=True, docsgenerate=False):
        """
        update content from source
        :param pull: means will update content from github
        :param docsgenerate: means will run the docsite generate, can take a while
        :return:
        """
        wikipath = j.clients.git.getContentPathFromURLorPath(urlOrPath=self.giturl, pull=pull)
        if docsgenerate:
            j.shell()


class Wikis(j.application.JSBaseConfigsClass):

    _CHILDCLASS = Wiki
