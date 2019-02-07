lapis = require "lapis"
  
class ChatApp extends lapis.Application
    @path: "/chat"
    @name: "chat_"
    @enable "etlua"

    [index: "/session/:topic"]: =>
        req = @req.parsed_url
        scheme = "ws"
        if req.scheme == "https"
            scheme = "wss"
        @url = scheme .. "://" .. req.host .. ":" .. req.port
        @topic = @params.topic
        render: "chat.index"
