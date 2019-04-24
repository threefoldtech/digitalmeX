# userbot

creates initialization token and only accessible by the bootstrap bot. It returns `user_initialization` record 

```
@url = threebot.user.initialization
name* = "" (S)
token = ""(S)
```


## methods


### initialization_token
returns initialization token and it requires `BOOTSTRAP_TOKEN` environment variable to access the initialization token.
