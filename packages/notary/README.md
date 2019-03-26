# Threefold Notary

## How to run

We assume you have jumpscaleX and digitalmeX installed.

The notary expect to have access to a 0-db namespace. Make sure to create one before starting the notary.
Then you can use the notary CLI to start the notary gedis process:
```bash
notary gedis --listen :5000 --zdb localhost:9900 --namespace notary --secret 0dbsecret
```
This command will start the notary gedis process. Notary will listen on all interfaces and port 5000.
It will connect to the 0-db running at `localhost` and port `5000` and use the namespace called `notary` protected by the password `0dbsecret`

To have the REST interface of the notary, you need to also run lapis.
```
notary lapis --port 8080 --gedis localhost:5000
```
This command will start lapis on port `8080` and make lapis connect to the notary gedis actor on `localhost:5000`

## How to use it

## to register

### using gedis

```
gedis_client = j.clients.gedis.get("notary", port=8888)
gedis_client.cmds.notary_actor.register("123", "aa==","{{CONTENT_SIGNATURE}}")
```
### using curl
```
curl -d '{"threebot_id":"123","content":"aa==", "content_signature":"{{CONTENT_SIGNATURE}}"}' -H "Content-Type: application/json" -X POST http://localhost:8080/register
```
## to get
### using gedis

```
gedis_client = j.clients.gedis.get("notary", port=8888)
gedis_client.cmds.notary_actor.get("21491a8b3d97ad5b705e3be26e7")
```

### from browser
```
http://localhost:8080/get?hash="21491a8b3d97ad5b705e3be26e7"
```
