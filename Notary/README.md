# How to run Notary 
## in kosmos run the following: 
```python

server = j.servers.gedis.configure(host="0.0.0.0", port=8888)

server.actor_add('/sandbox/code/github/threefoldtech/digitalmeX/Notary/actors/notary_actor.py') 

server.start()                                            
```
## using Tmux
```
cd /sandbox/code/github/threefoldtech/digitalmeX/Notary/

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
http://localhost:8080/delete?robot_id="123",key="test",key_signature="Notary_test"
```
