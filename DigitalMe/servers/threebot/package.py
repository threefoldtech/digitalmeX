def install():
    rack = j.servers.rack.get()
    app = j.servers.gedis_websocket.default.app
    rack.websocket_server_add("websocket", 4444, app)
    dns = j.servers.dns.get_gevent_server("main", port=5354)  # for now high port
    rack.add("dns", dns)
    _gedis_server = j.servers.gedis.get("main", port=8900)
    rack.add("gedis", _gedis_server.gedis_server)
    rack.bottle_server_add()


def uninstall():
    pass  # For Now
    raise j.exceptions.Base("not implemented yet")


def prepare():
    pass  # For Now
    raise j.exceptions.Base("not implemented yet")


def update():
    pass  # For Now
    raise j.exceptions.Base("not implemented yet")
