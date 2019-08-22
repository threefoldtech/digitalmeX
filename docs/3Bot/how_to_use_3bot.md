# How to use 3bot


## Prerequisites
- Install sonic

    `j.servers.threebot.install()`

## Components of 3bot
- Servers: zdb , wikis_loader, sonic
- Actors: Classes that include functionalities that will be called by the client 
- Packages: Classes that tell threebot what to serve e.g. actors and how. see more at [Packages](https://github.com/threefoldtech/digitalmeX/blob/development_jumpscale/DigitalMe/servers/threebot/README.md)

## Steps to use 3bot

## __Example 1__ : To use threebot with an actor that returns hello when used
### __Start 3bot server__
Get an instance from threebot server that can be used:

    threebot_server = j.servers.threebot.get("3bot_hello")
    threebot_server.start()
_where_ threebot server name is "3bot_hello"

### __Create actor__
The actor will include all the functionalities needed, in our case a function that returns hello when called: 
```
#actor_hello.py
from Jumpscale import j

class actor_hello(j.application.ThreeBotActorBase):
    def _init(self, **kwargs):
        pass

    def hello(self, name):
        print("hello %s" % name)
```

_note_ : it can be added in a directory such as test_hello folder in digitalmeX: 
```
├── threebot
│   └── packages
│       └── threefold
│           └── test_hello
│               ├── actors
│               │   ├── actor_hello.py
│               ├── package.py

```


The actor is loaded to gedis instance of the package created using the following command:
    
    self.gedis_server.actor_add(path_to_actor)
or if there are multiple actors to be loaded:

    self.gedis_server.actors_add(path_to_actors_directoryss)   



### __Create package__
The package will be used to load the actor and provide how it will be used. It should include the following functions:
```
#package.py
from Jumpscale import j

class Package(j.application.ThreeBotPackageBase):
    def prepare(self):
        """
        is called at install time
        :return:
        """
        name = "hello_test"
        if not j.data.bcdb.exists(name=name):
            zdb_admin = j.clients.zdb.client_admin_get()
            zdb = zdb_admin.namespace_new(name, secret="123456")
            bcdb = j.data.bcdb.new(name=name, storclient=zdb)
        else:
            bcdb = j.data.bcdb.get(name=name)

    def start(self):
        """
        called when the 3bot starts
        :return:
        """
        #ADDING ACTOR TO GEDIS
        self.gedis_server.actors_add(j.sal.fs.joinPaths(self.package_root, "actors/actor_hello.py"))
        pass

    def stop(self):
        """
        called when the 3bot stops
        :return:
        """
        pass

    def uninstall(self):
        """
        called when the package is no longer needed and will be removed from the threebot
        :return:
        """
        pass
```
### __Load package__
```
package = j.tools.threebotpackage.get("package_hello",
                                path="/sandbox/code/github/threefoldtech/digitalmeX/threebot/packages/threefold/test_hello",
                            threebotserver_name="3bot_hello")

```
where `package` instance can be later retrieved by `j.tools.threebotpackage.package_hello`
### __Call actor__
To get an instance of the actor _actor_hello_ to be used from the package loaded:
```
    actor = j.clients.gedis.get("threebot_test",host=ip_address,port=port).actor_hello
```
where 
- _ip_address_ : ip address gedis server of the package is running on
- _port_ : port gedis server of the package is listening on

