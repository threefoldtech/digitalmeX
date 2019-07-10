# bot_init chatflow


chatflow for initializing the 3bot [specs](https://github.com/threefoldfoundation/3bot/blob/master/specs/initialize.md)


## Starting
- link the actors
```
ln /sandbox/code/github/threefoldtech/digitalmeX/packages/init_bot/actors/* -s /sandbox/code/github/threefoldtech/digitalmeX/DigitalMe/tools/openpublish/base_actors/
```

- link the chatflow
```
ln /sandbox/code/github/threefoldtech/digitalmeX/packages/init_bot/chatflows/*.py -s /sandbox/code/github/threefoldtech/digitalmeX/DigitalMe/tools/openpublish/base_chatflows/

```
- make sure to run openpublish tool
`js_shell 'j.servers.threebot.default.servers_start()'`



### notes
- only one instance of `tfchain` client
- only one instance of `tfchain.wallet`
- access requires the initialization token

Example on how to get the initialization token
```python
def get_init_token():
    # get initialization token from user 3bot
    BCDB_NAMESPACE = "threebotuser"

    bcdb = j.servers.threebot.bcdb_get(
        BCDB_NAMESPACE, use_zdb=True)
    bcdb.models_add(
        "/sandbox/code/github/threefoldtech/digitalmeX/packages/init_bot/models")

    user_bot_model = bcdb.model_get(
        'threebot.user.initialization')

    user_settings = user_bot_model.get_by_name('user_initialization')
    if not user_settings:
        raise RuntimeError('Initialization token is not set')
    print("user_settings[0].token", user_settings[0].token)
    return user_settings[0].token

```
