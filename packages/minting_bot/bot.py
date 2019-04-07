from Jumpscale import j
from telegram import ParseMode

TEMPLATES_DIR = "/sandbox/code/github/threefoldtech/digitalmeX/packages/minting_bot/templates"

directory = j.tools.threefold_directory
# directory.scan()


def render_template(template, **kwargs):
    return j.tools.jinja2.template_render(path=j.sal.fs.joinPaths(TEMPLATES_DIR, template), **kwargs)


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def respond_html(update, context, content):
    return context.bot.send_message(chat_id=update.message.chat_id, text=content, parse_mode=ParseMode.HTML)


def start(update, context):
    content = "<i>Hello</i> I'm ThreeFoldToken minting bot, to get a list of what I can do please send /help"
    respond_html(update, context, content)


def list_farmers(update, context):
    try:
        farmers = directory.farmers.findData()
        for chunk in chunks(farmers, 20):
            content = render_template("farmers.html", farmers=chunk)

            respond_html(update, context, content)
    except Exception as e:
        print(e)

def list_nodes_farmer(update, context):
    try:
        if not context.args:
            respond_html(update, context, "Sorry but I didn't get it, please provide a farmer ID, example:-  "
                                          "/list_nodes_farmer 123")
            return
        farmer_id = ' '.join(context.args)
        nodes = directory.nodes.findData(farmer_id=farmer_id)
        if not nodes:
            respond_html(update, context, "Sorry but I couldn't find any up nodes for the provided farmer ID")
            return

        for chunk in chunks(nodes, 20):
            content = render_template("nodes.html", nodes=chunk)
            respond_html(update, context, content)
    except Exception as e:
        print(e)

def node_info(update, context):
    try:
        if not context.args:
            respond_html(update, context, "Sorry but I didn't get it, please provide a Node ID, example:-  "
                                          "/node_details 123")
            return
        node_id = context.args[0]
        node = directory.nodes.get(name="tf_{}".format(node_id))
        content = render_template("node_details.html", node=node)
        respond_html(update, context, content)
    except Exception as e:
        print(e)

def help(update, context):
    text = render_template("help.html")
    context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=ParseMode.HTML)


def main():
    client = j.clients.telegram_bot.get("test", bot_token_="XXXX")

    client.command_register("start", start)
    client.command_register("help", help)
    client.command_register("list_farmers", list_farmers)
    client.command_register("list_nodes_farmer", list_nodes_farmer)
    client.command_register("node_info", node_info)
    print("bot starting ")
    client.start_polling()



main()