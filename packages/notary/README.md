# How to run Notary 
## in kosmos run the following: 
```python

zdb_cl = j.clients.zdb.start_test_instance()
zdb_cl = zdb_cl.namespace_new("notary_namespace", secret="1234")
bcdb = j.data.bcdb.new(zdbclient=zdb_cl, name="notary_bcdb")
bcdb.models_add("/sandbox/code/github/threefoldtech/digitalmeX/packages/notary/models")
server = j.servers.gedis.configure(host="0.0.0.0", port=8888)
server.actor_add('/sandbox/code/github/threefoldtech/digitalmeX/packages/notary/actors/notary_actor.py')
server.models_add(models=bcdb.models.values())
server.start()                                          
```
## using Tmux
```
cd /sandbox/code/github/threefoldtech/digitalmeX/packages/notary

moonc . &&lapis server
```

# How to use it

## to register
```
curl -d '{"robot_id":"123", "key":"test", "content":"Notary", "content_signature":"Notary_test"}' -H "Content-Type: application/json" -X POST http://localhost:8080/register
```
## to get 
```
http://localhost:8080/get?key="test"
```

## to delete 
```
http://localhost:8080/delete?robot_id="123"&key="test"&content_signature="Notary_test"
```
