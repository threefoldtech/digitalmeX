# bootstrap_bot

used to deploy 3bots [specs](https://github.com/threefoldfoundation/3bot/blob/master/specs/register.md)




## Bootstrapping bot
- Bootstrap bot chooses the nearest farm to the user's location
- Sets the initialization token on the freshly deployed `userbot` and sending email back with information on initializing new 3bot

## Sending emails
The bootstrap bot requires `SENDGRID_API_KEY` to send emails to 3bot owners
