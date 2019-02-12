lapis = require "lapis"
  
class ChatApp extends lapis.Application
    @path: "/chat"
    @name: "chat_"
    @enable "etlua"

    [index: "/session/:topic"]: =>
        req = @req.parsed_url
        scheme = "ws"
        if req.scheme == "https" or @req.headers['x-forwarded-proto'] == "https"
            scheme = "wss"
        @url = scheme .. "://" .. req.host
        @topic = @params.topic
        render: "chat.index"
