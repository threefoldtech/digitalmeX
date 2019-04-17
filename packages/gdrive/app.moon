lapis = require "lapis"
redis = require 'redis'
config = require("lapis.config").get!
util = require "lapis.util"
msgpack = require("MessagePack")
encoding = require "lapis.util.encoding"
import capture_errors_json, yield_error, assert_error from require "lapis.application"


class extends lapis.Application
  @enable "etlua"

  "/:type/:guid1(/:guid2)": =>
    print "type>>>"
    print @params.type
    print "type>>>"
    print @params.guid1
    print "type>>>"
    print @params.guid2
    ngx.req.read_body()
    data = ngx.req.get_body_data()
    client = redis.connect(config.gedis_host, config.gedis_port)
    
    header = {"response_type": "msgpack"}
    resp = redis.command("default.gdrive.file_get")(client, util.to_json(data), util.to_json(header))
    decoded = mp.unpack(resp)
    
    response = {
      "json": decoded,
      "status": 201
    }
    return response