# running
```
 kosmos 'j.servers.gundb._server_test_start()'
```

### usage with bcdb

assuming you have these schemas registered in your system

```
bcdb = j.data.bcdb.get(name="test")
bcdb.reset()
j.data.schema.add_from_text("""
@url = proj.todo
title* = "" (S)
done* = False (B)

""")

j.data.schema.add_from_text("""
@url = proj.todolist
name* = "" (S)
todos* = (LO) !proj.todo

""")
j.data.schema.add_from_text("""
@url = proj.simple
attr1* = "" (S)
attr2* = 0 (I)
mychars* = (LS) 
""")

j.data.schema.add_from_text("""
@url = proj.email
addr* = "" (S)
""")
j.data.schema.add_from_text("""
@url = proj.person
name* = "" (S)
email* = "" !proj.email
""")


j.data.schema.add_from_text("""
@url = proj.os
name* = "" (S)
""")


j.data.schema.add_from_text("""
@url = proj.phone
model* = "" (S)
os* = "" !proj.os
""")


j.data.schema.add_from_text("""
@url = proj.human
name* = "" (S)
phone* = "" !proj.phone
""")


```
you can use them from your javascript code using `gun.js` client

```javascript
    <script src="https://cdn.jsdelivr.net/npm/gun/gun.js"></script>

      var gun = Gun("ws://172.17.0.2:7766/gun")

      gun.get("proj.human://1").put({"name":"xmon"})
      gun.get("proj.human://1").get("phone").put({
          "model":"samsung"
      })
      gun.get("proj.human://1").get("phone").get("os").put({
          "name":"android"
      })

      gun.get("proj.human://2").put({"name":"richxmon"})
      gun.get("proj.human://2").get("phone").put({
          "model":"iphone"
      })
      gun.get("proj.human://2").get("phone").get("os").put({
          "name":"ios"
      })
```

in the server output logs you see something like

```
success.....!!!!! id = 1
name = "xmon"
phone = "{'model': 'samsung', 'os': {'name': 'android'}}"

success.....!!!!! id = 2
name = "richxmon"
phone = "{'model': 'iphone', 'os': {'name': 'ios'}}"

```


there're some test scripts in html directory make sure to update the gun server endpoint