# sonic actor

Used to access sonic client in jumpscaleX


# methods

## query

```query(collection, bucket, text)```
query takes in collection, bucket and text and returns list of objects where the text exists


# Example in Javascript

```
sonic_search = function (name, query)
{
    var info = {
        "namespace": "default",
        "actor": "sonic",
        "command": "query",
        "args": {"collection":"docsites", "bucket":name, "text":query},
        "headers": {"response_type":"json"}
    }
    return GEDIS_CLIENT.execute(info)
}
```