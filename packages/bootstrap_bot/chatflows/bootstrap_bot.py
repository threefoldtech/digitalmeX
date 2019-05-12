import logging
import pycountry
import json
import os
import time

from geopy.geocoders import Nominatim
from geopy.distance import geodesic

from logging import NullHandler
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from Jumpscale import j


logger = logging.getLogger('bootstrap_bot')
logger.addHandler(NullHandler())
logger.setLevel(20)


def get_userbot(location):
    capacity = j.clients.threefold_directory.get(interactive=False)
    resp = capacity.api.ListFarmers()[1]
    resp.raise_for_status()
    farmers = resp.json()

    geolocator = Nominatim(user_agent='bootstrap_bot')
    user_location = geolocator.geocode({'country': location})

    # location_farmers is a dict where the key is location proximity and the value is a list of farmers in this location proximity
    locations_farmers = dict()

    for farmer in farmers:
        if 'location' not in farmer:
            continue
        farmer_location = (farmer['location']['latitude'], farmer['location']['longitude'])
        distance = geodesic((user_location.latitude, user_location.longitude), farmer_location).km
        if distance in locations_farmers:
            locations_farmers[distance].append(farmer)
        else:
            locations_farmers[distance] = [farmer]

    bot_id = j.data.idgenerator.generateGUID()
    bootstrap_token = j.data.idgenerator.generateGUID()
    init_token = None

    sorted_locations = sorted(locations_farmers.keys())
    for distance in sorted_locations:
        for farmer in locations_farmers[distance]:
            farm = j.sal_zos.farm.get(farmer['iyo_organization'])
            logger.info("Checking farmer %s" % farmer['iyo_organization'])
            nodes = sort_by_less_used(list(farm.filter_online_nodes()))
            # this farm has no online nodes, move on to the next farm
            if not nodes:
                continue

            for node in nodes:
                logger.info("Getting node with id %s" % node['node_id'])
                logger.info("Bootstrap token %s" % bootstrap_token)
                node_sal = j.clients.zos.get_by_id(node['node_id'])

                try:
                    ports = node_sal.client.socat.reserve(2)
                    userbot = None
                    userbot = j.sal_zos.userbot.get(node_sal, bot_id, bootstrap_token, ports[0], ports[1])
                    userbot.start()
                except Exception as e:
                    # failed to create/start the 3bot container, continue and try another node
                    logger.info("Failed to start node %s, continue and try another node: %s" % (node['node_id'], str(e)))
                    if userbot:
                        userbot.destroy()
                    continue

                # get initialization token from user 3bot
                now = time.time()
                while True:
                    try:
                        cli = j.clients.redis.get(ipaddr=node_sal.addr, port=ports[0])
                        init_token = cli.execute_command('default.userbot.initialization_token', '{"bootstrap_token": "%s"}' % bootstrap_token)
                        break
                    except Exception as e:
                        logger.info("Couldn't connect to actor on node %s: %s" % (node['node_id'], str(e)))
                        if time.time() < now + 600:
                            logger.info("Wait a bit more for node %s to respond" % node['node_id'])
                            time.sleep(30)
                        else:
                            logger.info("Time is up, destroying node %s and trying another node" % node['node_id'])
                            userbot.destroy()
                            break
                if not init_token:
                    continue
                init_token = init_token.decode()
                return init_token, node_sal.addr, userbot.lapis_port, bootstrap_token

    return None, None, None, None

def chat(bot):
    """
    to call http://localhost:5050/chat/session/bootstrap_bot
    """
    email = bot.string_ask('Enter your email', validate={'required':True, 'email': True})
    location = bot.drop_down_choice('Choose your location: ',  [c.name for c in pycountry.countries], validate={'required':True})
    captcha = False
    error = False
    while not captcha:
        captcha = bot.captcha_ask(error, validate={'required':True})
        error = True


    init_token, ip, port, bootstrap_token = get_userbot(location)

    if not init_token:
        R = """"
        Failed to find a suitable node for installing your 3bot
        """
        bot.md_show(R)
        return

    bot_url = "http://%s:%s/chat/session/bot_init" % (ip, port)

    content = """
    You have ordered 3bot for email {{email}}, near location {{location}}.
    Please go to {{bot_url}} and use {{init_token}} to initialize your 3bot.
    """

    message = Mail(
        from_email="info@threefoldtech.com",
        to_emails=email,
        subject='3bot Initialization',
        html_content=j.tools.jinja2.template_render(text=j.core.text.strip(content),**locals()))
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
    except Exception as e:
        logger.error(str(e))

    R = """
    You have ordered 3bot for email {{email}}, near location {{location}}.

    Click next to be redirected to your 3bot initiliazation page
    and use this token for initialization: {{init_token}}
    """

    R2 = j.tools.jinja2.template_render(text=j.core.text.strip(R),**locals())
    bot.md_show(R2)
    bot.redirect(bot_url)



def sort_by_less_used(nodes):
    def key(node):
        return (-node['total_resources']['cru'],
                -node['total_resources']['mru'],
                -node['total_resources']['sru'],
                node['used_resources']['cru'],
                node['used_resources']['mru'],
                node['used_resources']['sru'])
    return sorted(nodes, key=key)


