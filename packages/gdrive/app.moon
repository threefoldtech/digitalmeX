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

    data = {
        "doctype": @params.type,
        "guid1": @params.guid1,
        "guid2": @params.guid2,
    }
    client = redis.connect(config.gedis_host, config.gedis_port)
    
    header = {"response_type": "msgpack"}
    resp = redis.command("default.gdrive.file_get")(client, util.to_json(data), util.to_json(header))
    decoded = msgpack.unpack(resp)
    redirect_to: decoded["res"]