local lapis = require("lapis")
local redis = require('redis')
local config = require("lapis.config").get()
local util = require("lapis.util")
local msgpack = require("MessagePack")
local encoding = require("lapis.util.encoding")
local capture_errors_json, yield_error, assert_error
do
  local _obj_0 = require("lapis.application")
  capture_errors_json, yield_error, assert_error = _obj_0.capture_errors_json, _obj_0.yield_error, _obj_0.assert_error
end
do
  local _class_0
  local _parent_0 = lapis.Application
  local _base_0 = {
    ["/"] = function(self)
      local client = redis.connect(config.gedis_host, config.gedis_port)
      return redis.command("default.notary_actor.start_page")(client)
    end,
    ["/register"] = function(self)
      ngx.req.read_body()
      local data = ngx.req.get_body_data()
      local client = redis.connect(config.gedis_host, config.gedis_port)
      local header = {
        ["response_type"] = "msgpack"
      }
      local resp = redis.command("default.notary_actor.register")(client, util.to_json(data), util.to_json(header))
      local decoded = mp.unpack(resp)
      header = {
        ["response_type"] = "msgpack"
      }
      local response = {
        ["json"] = decoded,
        ["status"] = 201
      }
      return response
    end,
    ["/get"] = function(self)
      ngx.req.read_body()
      local client = redis.connect(config.gedis_host, config.gedis_port)
      local args = {
        ["hash"] = self.params.hash
      }
      local header = {
        ["response_type"] = "msgpack"
      }
      local resp = redis.command("default.notary_actor.get")(client, util.to_json(args), util.to_json(header))
      print(resp)
      local decoded = msgpack.unpack(resp)
      decoded.id = nil
      decoded.content = encoding.encode_base64(decoded.content)
      decoded.content_signature = encoding.encode_base64(decoded.content_signature)
      local response = {
        ["json"] = decoded,
        ["status"] = 200
      }
      return response
    end
  }
  _base_0.__index = _base_0
  setmetatable(_base_0, _parent_0.__base)
  _class_0 = setmetatable({
    __init = function(self, ...)
      return _class_0.__parent.__init(self, ...)
    end,
    __base = _base_0,
    __name = nil,
    __parent = _parent_0
  }, {
    __index = function(cls, name)
      local val = rawget(_base_0, name)
      if val == nil then
        local parent = rawget(cls, "__parent")
        if parent then
          return parent[name]
        end
      else
        return val
      end
    end,
    __call = function(cls, ...)
      local _self_0 = setmetatable({}, _base_0)
      cls.__init(_self_0, ...)
      return _self_0
    end
  })
  _base_0.__class = _class_0
  if _parent_0.__inherited then
    _parent_0.__inherited(_parent_0, _class_0)
  end
  return _class_0
end
