lapis = require "lapis"
redis = require 'redis'
config = require("lapis.config").get!
util = require "lapis.util"
msgpack = require("MessagePack")
encoding = require "lapis.util.encoding"
import capture_errors_json, yield_error, assert_error from require "lapis.application"


class extends lapis.Application
  @enable "etlua"
  "/": =>
    render: "index"

  "/register": =>
    ngx.req.read_body()
    data = ngx.req.get_body_data()
    client = redis.connect(config.gedis_host, config.gedis_port)

    header = {"response_type": "msgpack"}
    resp = redis.command("default.notary_actor.register")(client, util.to_json(data), util.to_json(header))
    decoded = mp.unpack(resp)

    header = {"response_type": "msgpack"}
    response = {
      "json": decoded,
      "status": 201
    }
    return response


  "/get":  =>
    ngx.req.read_body()
    client = redis.connect(config.gedis_host, config.gedis_port)

    args = {"hash": @params.hash}
    header = {"response_type": "msgpack"}
    resp = redis.command("default.notary_actor.get")(client, util.to_json(args), util.to_json(header))
    print(resp)
    decoded = msgpack.unpack(resp)

    decoded.id = nil
    decoded.content = encoding.encode_base64(decoded.content)
    decoded.content_signature = encoding.encode_base64(decoded.content_signature)

    response = {
      "json": decoded,
      "status": 200
    }
    return response