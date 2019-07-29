

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
        j.sal.fs.writeFile("%s/servers/proxy_%s.conf" % (self._parent._parent._web_path, self.name), r)


class ReverseProxies(j.application.JSBaseConfigsClass):

    _CHILDCLASS = ReverseProxy
