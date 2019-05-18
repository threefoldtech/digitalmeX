from Jumpscale import j
from telegram import ParseMode

"""
Minting Telgram bot

How to run:
python3 /sandbox/code/github/threefoldtech/digitalmeX/packages/minting_bot/bot.py

you may need to install python-telegram-bot version 12.0.0
pip3 install python-telegram-bot==12.0.0b1 --upgrade
"""

TEMPLATES_DIR = "/sandbox/code/github/threefoldtech/digitalmeX/packages/minting_bot/templates"

directory = j.tools.threefold_directory
# this should only run once to populate bcdb with farmers and nodes data
# directory.scan()


def print_error(func):
    """
    Python telegram bot methods ignores exceptions in order not to block the thread, this decorator is to print any
    exception happened in the method to make debugging easier
    """

    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            print(e)

    return wrapper


def render_template(template, **kwargs):
    """
    Renders a template with givin data
    :param template: the template file name without the directory, the template file sould be located in TEMPLATES_DIR
    :param kwargs: key value args to be rendered
    :return: rendered content
    """
    return j.tools.jinja2.template_render(path=j.sal.fs.joinPaths(TEMPLATES_DIR, template), **kwargs)


def chunks(l, n):
    """
    Yield successive n-sized chunks from list
    """
    for i in range(0, len(l), n):
        yield l[i : i + n]


def respond_html(update, context, content):
    """
    Sends html response to telegram
    """
    return context.bot.send_message(chat_id=update.message.chat_id, text=content, parse_mode=ParseMode.HTML)


@print_error
def start(update, context):
    """
    Start method, the greeting message that will be sent to the user once he started a chat with the bot
    """
    content = "<i>Hello</i> I'm ThreeFoldToken minting bot, to get a list of what I can do please send /help"
    respond_html(update, context, content)


@print_error
def list_farmers(update, context):
    """
    List all farmers
    """
    farmers = directory.farmers.findData()
    for chunk in chunks(farmers, 20):
        content = render_template("farmers.html", farmers=chunk)

        respond_html(update, context, content)


@print_error
def list_nodes_farmer(update, context):
    """
    List all nodes for a given farmer
    """
    if not context.args:
        respond_html(
            update,
            context,
            "Sorry but I didn't get it, please provide a farmer ID, example:-  " "/list_nodes_farmer 123",
        )
        return
    farmer_id = " ".join(context.args)
    nodes = directory.nodes.findData(farmer_id=farmer_id)
    if not nodes:
        respond_html(update, context, "Sorry but I couldn't find any up nodes for the provided farmer ID")
        return

    for chunk in chunks(nodes, 20):
        content = render_template("nodes.html", nodes=chunk)
        respond_html(update, context, content)


@print_error
def node_info(update, context):
    """
    Display node data
    #TODO: now it display very basic info we should show more data in human readable format
    """
    if not context.args:
        respond_html(
            update, context, "Sorry but I didn't get it, please provide a Node ID, example:-  " "/node_details 123"
        )
        return
    node_id = context.args[0]
    node = directory.nodes.get(name="tf_{}".format(node_id))
    content = render_template("node_details.html", node=node)
    respond_html(update, context, content)


@print_error
def help(update, context):
    """
    Displays help message
    """
    text = render_template("help.html")
    context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=ParseMode.HTML)


def main():

    client = j.clients.telegram_bot.get("test", bot_token_="XXXX")
    client.command_register("start", start)
    client.command_register("help", help)
    client.command_register("list_farmers", list_farmers)
    client.command_register("list_nodes_farmer", list_nodes_farmer)
    client.command_register("node_info", node_info)
    print("bot starting ...")
    client.start_polling()


main()
