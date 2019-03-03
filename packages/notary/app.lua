local lapis = require("lapis")
local redis = require('redis')
local config = require("lapis.config").get()
local util = require("lapis.util")
do
  local _class_0
  local _parent_0 = lapis.Application
  local _base_0 = {
    ["/"] = function(self)
      local client = redis.connect(config.gedis_host, config.gedis_port)
      client["gedis"] = redis.command("default.notary_actor.start_page")
      return client.gedis(client)
    end,
    ["/register"] = function(self)
      ngx.req.read_body()
      local data = ngx.req.get_body_data()
      local client = redis.connect(config.gedis_host, config.gedis_port)
      client["gedis"] = redis.command("default.notary_actor.register")
      local header = {
        ["response_type"] = "json"
      }
      return client.gedis(client, util.to_json(data), util.to_json(header))
    end,
    ["/get"] = function(self)
      ngx.req.read_body()
      local client = redis.connect(config.gedis_host, config.gedis_port)
      client["gedis"] = redis.command("default.notary_actor.get")
      local args = {
        ["key"] = self.params.key
      }
      local header = {
        ["response_type"] = "json"
      }
      return client.gedis(client, util.to_json(args), util.to_json(header))
    end,
    ["/delete"] = function(self)
      ngx.req.read_body()
      local client = redis.connect(config.gedis_host, config.gedis_port)
      client["gedis"] = redis.command("default.notary_actor.delete")
      local args = {
        ["threebot_id"] = self.params.threebot_id,
        ["key"] = self.params.key,
        ["content_signature"] = self.params.content_signature
      }
      local header = {
        ["response_type"] = "json"
      }
      return client.gedis(client, util.to_json(args), util.to_json(header))
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
