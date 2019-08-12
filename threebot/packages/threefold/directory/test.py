from Jumpscale import j

zdb = j.servers.zdb.get("threebot")

# SAME BEHAVOUR WITH RESTART OR NOT

# zdb.stop()
# zdb.start()

zdb_admin = j.clients.zdb.client_admin_get()

# zdb_admin.reset()

# zdb_admin.namespace_new("directory", secret="123456")

# j.data.schema.add_from_path("/sandbox/lib/jumpscale/threebot/packages/threefold/directory")

zdb = j.clients.zdb.get("threebot", port=9900, nsname="directory", secret_="123456")

zdb.flush()

zdb.set("1")
zdb.set("2")
zdb.set("3")

zdb.set("b", 2)
zdb.set("c", 2)
zdb.set("c", 2)
zdb.set("b", 2)
