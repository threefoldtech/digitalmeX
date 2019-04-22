import logging
import pycountry
import json
import os

from geopy.geocoders import Nominatim
from geopy.distance import geodesic

from logging import NullHandler

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from Jumpscale import j


logger = logging.getLogger('bootstrap_bot')
logger.addHandler(NullHandler())
logger.setLevel(20)


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
        if init_token:
            break
        for farmer in locations_farmers[distance]:
            if init_token:
                break
            farm = j.sal_zos.farm.get(farmer['iyo_organization'])
            nodes = sort_by_less_used(list(farm.filter_online_nodes()))
            # this farm has no online nodes, move on to the next farm
            if not nodes:
                continue

            for node in nodes:
                node_sal = j.clients.zos.get_by_id(node['node_id'])
                ports = node_sal.client.socat.reserve(2)
                userbot = j.sal_zos.userbot.get(node_sal, bot_id, bootstrap_token, ports[0], ports[1])
                try:
                    userbot.start()
                except RuntimeError:
                    # failed to create/start the 3bot container, continue and try another node
                    userbot.destroy()
                    continue

                # get initialization token from user 3bot
                redis = j.clients.redis.get(ip_addr=node.addr, port=ports[0])
                init_token = redis.execute_command('default.userbot.initialization_token', '{"key": "%s"}' % bootstrap_token)
                init_token = json.loads(init_token.decode())['token']
                break

    if not init_token:
        R = """"
        Failed to find a suitable node for installing you 3bot
        """
    else:
        R = """
        # You have ordered 3bot for email {{email}}, near location {{location}}:

        ### Click next

        for the final step which will redirect you to your 3bot initiliazation page
        and use this token for initialization {{init_token}}
        """

    R2 = j.tools.jinja2.template_render(text=j.core.text.strip(R),**locals())

    bot.md_show(R2)

    if not init_token:
        return

    email = """
    You have ordered 3bot for email {{email}}, near location {{location}}.
    Please go to {{bot_url}} and use {{init_token}} to initialize your 3bot.
    """
    message = Mail(
        from_email="info@threefoldtech.com",
        to_emails=email,
        subject='3bot Initialization',
        html_content=email)
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
    except Exception as e:
        logger.error(e.message)

    bot_url = "http://%s:8080/chat/session/initialize_bot"
    bot.redirect(bot_url)



def sort_by_less_used(nodes):
    def key(node):
        return (-node['total_resources']['cru'],
                -node['total_resources']['mru'],
                -node['total_resources']['hru'],
                node['used_resources']['cru'],
                node['used_resources']['mru'],
                node['used_resources']['hru'])
    return sorted(nodes, key=key)


