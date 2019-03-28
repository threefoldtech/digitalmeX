lapis = require "lapis"
  
class ChatApp extends lapis.Application
    @path: "/chat"
    @name: "chat_"
    @enable "etlua"

    [root: "/"]: =>
        redirect_to: "/session/deploy_website"

    [index: "/session/:topic"]: =>
        req = @req.parsed_url
        scheme = "ws"
        if req.scheme == "https" or @req.headers['x-forwarded-proto'] == "https"
            scheme = "wss"
        @url = scheme .. "://" .. req.host
        if req.port
            @url = @url .. ":" .. req.port
        @topic = @params.topic
        render: "chat.index"
