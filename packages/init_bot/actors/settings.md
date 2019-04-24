# settings actor

used to manage threebot profile settings around `threebot_user_settings` schema


```


@url = threebot.user.settings
doubleName* = ""
firstName* = ""
lastName = ""
email* = ""
addressStreet = ""
addressNumber = ""
addressZipcode = ""
addressCity = ""
addressCountry* = ""
telephone = ""


```

## methods

### get_threebotsettings
returns the `threebot.user.settings` 


### update_threebotsettings

update the bot settings record (with verification from [3botlogin](https://github.com/3botlogin/3botlogin))