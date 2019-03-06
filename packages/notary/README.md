# How to run Notary 
## in kosmos run the following: 
```python
j.builder.db.zdb.start() 
zdb_cl = j.clients.zdb.client_admin_get()  
zdb_cl = zdb_cl.namespace_new("notary_namespace", secret="1234")
bcdb = j.data.bcdb.new(zdbclient=zdb_cl, name="notary_bcdb")
bcdb.models_add("/sandbox/code/github/threefoldtech/digitalmeX/packages/notary/models")
server = j.servers.gedis.configure(host="0.0.0.0", port=8888)
server.actor_add('/sandbox/code/github/threefoldtech/digitalmeX/packages/notary/actors/notary_actor.py')
server.models_add(models=bcdb.models.values())
server.save()
server.start()                                          
```
## using Tmux
```
cd /sandbox/code/github/threefoldtech/digitalmeX/packages/notary

moonc . &&lapis server
```

# How to use it

## to register

### using gedis

```
gedis_client = j.clients.gedis.get("notary", port=8888) 
gedis_client.cmds.notary_actor.register("123","test","Notary","{{CONTENT_SIGNATURE}}") 
```
### using curl 
```
curl -d '{"robot_id":"123", "key":"test", "content":"Notary", "content_signature":"{{CONTENT_SIGNATURE}}"}' -H "Content-Type: application/json" -X POST http://localhost:8080/register
```
## to get 
### using gedis

```
gedis_client = j.clients.gedis.get("notary", port=8888) 
gedis_client.cmds.notary_actor.get("test") 
```

### from browser
```
http://localhost:8080/get?key="test"
```
