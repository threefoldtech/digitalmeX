

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
        j.sal.fs.writeFile("%s/servers/%s.conf" % (self._parent._parent._web_path, self.name), r)


class Websites(j.application.JSBaseConfigsClass):

    _CHILDCLASS = Website
