lapis = require "lapis"
redis = require 'redis'
config = require("lapis.config").get!
util = require "lapis.util"

class extends lapis.Application
  "/": =>
    client = redis.connect(config.gedis_host, config.gedis_port)
    client["gedis"] = redis.command("default.notary_actor.start_page")
    client.gedis(client)
    
  "/register": =>
    ngx.req.read_body()
    data = ngx.req.get_body_data()

    client = redis.connect(config.gedis_host, config.gedis_port)
    client["gedis"] = redis.command("default.notary_actor.register")

    header = {
      "response_type": "json"
    }
    client.gedis(client, util.to_json(data), util.to_json(header))
    

  "/get": =>
    ngx.req.read_body()
    client = redis.connect(config.gedis_host, config.gedis_port)
    client["gedis"] = redis.command("default.notary_actor.get")

    args = {
      "key": @params.key
    }
    header = {
      "response_type": "json"
    }
    return client.gedis(client, util.to_json(args), util.to_json(header))

  "/delete": =>
    ngx.req.read_body()
    client = redis.connect(config.gedis_host, config.gedis_port)
    client["gedis"] = redis.command("default.notary_actor.delete")

    args = {
      "robot_id": @params.robot_id,
      "key": @params.key,
      "content_signature": @params.content_signature
    }
    header = {
      "response_type": "json"
    }
    return client.gedis(client, util.to_json(args), util.to_json(header))