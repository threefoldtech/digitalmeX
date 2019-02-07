# how to start chatbot

1- create links for static, views and applications directories to lapis wiki repo

```bash
ln -s /sandbox/code/github/threefoldtech/digitalmeX/packages/system/chat/lapis/static/chat /sandbox/code/github/threeefoldfoundation/lapis-wiki/static
ln -s /sandbox/code/github/threefoldtech/digitalmeX/packages/system/chat/lapis/views/chat /sandbox/code/github/threeefoldfoundation/lapis-wiki/views
ln -s /sandbox/code/github/threefoldtech/digitalmeX/packages/system/chat/lapis/applications/chat /sandbox/code/github/threeefoldfoundation/lapis-wiki/applications
```

2- setup and start gedis server in tmux
```python
server = j.servers.gedis.configure(host="{host}", port=8888) # will use port 8888 hardcoded for now
server.actor_add('/sandbox/code/github/threefoldtech/digitalmeX/packages/system/chat/actors/chatbot.py')
server.chatbot.chatflows_load('/sandbox/code/github/threefoldtech/digitalmeX/packages/system/base/chatflows/')
server.start()
```

3- start the web server
```python
j.tools.markdowndocs.webserver()
```