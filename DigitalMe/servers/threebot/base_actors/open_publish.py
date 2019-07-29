

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


import gevent
from Jumpscale import j

JSBASE = j.application.JSBaseClass


class open_publish(JSBASE):
    def _init(self, **kwargs):
        self.open_publish_tool = j.servers.threebot.default
        gevent.spawn(self.open_publish_tool.auto_update)

    def publish_wiki(self, name, repo_url, domain, ip):
        """
        ```in
        name = ""
        repo_url = ""
        domain = ""
        ip = "" (ipaddr)
        ```
        :param name: name of the wiki
        :param domain: domain name of wiki i.e.: mywiki.com
        :param repo_url: repository url that contains the docs
        :param ip: ip which the domain should point to
        :return:
        """
        self.open_publish_tool.add_wiki(name, repo_url, domain, ip)
        return True

    def publish_website(self, name, repo_url, domain, ip):
        """
        ```in
        name = ""
        repo_url = ""
        domain = ""
        ip = "" (ipaddr)
        ```
        :param name: name of the website
        :param domain: domain name of website i.e.: mywebsite.com
        :param repo_url: repository url that contains the website files
        :param ip: ip which the domain should point to
        :return:
        """
        self.open_publish_tool.add_website(name, repo_url, domain, ip)
        return True

    def remove_wiki(self, name):
        """
        ```in
        name = ""
        ```
        :param name: name of the wiki
        :return:
        """
        self.open_publish_tool.remove_wiki(name)
        return True

    def remove_website(self, name):
        """
        ```in
        name = ""
        ```
        :param name: name of the website
        :return:
        """
        self.open_publish_tool.remove_website(name)
