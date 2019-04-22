# Gdrive Package

This package provides endpoints for downloading and serving gdrive docs or slide

## available endpoint

`/doc/{doc_guid}`: downloads gdrive doc and redirect to it
`/slide/{presentation_guid}/{slide_guid}`: downloads the full presentation and redirect to the given slide


## How to start
**This is for development and will be changed**

to start this package you will need:
1- configure the main instance of gdrive client and make sure to provide a credentials file with the correct permissions
```python
cl = j.clients.gdrive.main
cl.cred_file = "{path_to_cred_file}"
```

2- integrate the lapis application into our open publishing framework
```bash
ln -s /sandbox/code/github/threefoldtech/digitalmeX/packages/gdrive/app.moon /sandbox/code/github/threefoldfoundation/lapis-wiki/applications/gdrive.moon
ln -s /sandbox/code/github/threefoldfoundation/lapis-wiki/static/gdrive /sandbox/var/gdrive/static/
```

3- create the needed dirs to store the files
```bash
mkdir -p /sandbox/var/gdrive/static
mkdir /sandbox/var/gdrive/static/doc
mkdir /sandbox/var/gdrive/static/slide
```

4- start gedis server with the actor loaded (you can use tmux)
```python
server = j.servers.gedis.get("{instance_name}", port=8888)
server.actor_add("/sandbox/code/github/threefoldtech/digitalmeX/packages/gdrive/actors/gdrive.py", "default")
server.start()
```
