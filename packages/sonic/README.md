# sonic actor

It's used to access [sonic client](https://github.com/threefoldtech/jumpscaleX/blob/master/Jumpscale/clients/sonic/README.md) in jumpscaleX


# methods

## query

```query(collection, bucket, text)```
query takes in collection, bucket and text and returns list of objects where the text exists


# Example in Javascript

To call function `query` on `actor` sonic with arguments `{"collection":"docsites", "bucket":name, "text":query}` using Gedis client for Javascript `GEDIS_CLIENT`
```


var info = {
        "namespace": "default",
        "actor": "sonic",
        "command": "query",
        "args": {"collection":"docsites", "bucket":"posts", "text":"lo"},
        "headers": {"response_type":"json"}
}
console.log(GEDIS_CLIENT.execute(info))
```


# Example in Python

```python
client.actors.sonic.query("forum", "posts", "love") 
```

client is `j.clients.gedis` object.