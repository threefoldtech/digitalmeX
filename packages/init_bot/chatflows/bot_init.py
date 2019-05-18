from Jumpscale import j
import os
import re
import geocoder
import pycountry
from pycountry_convert import country_alpha2_to_continent_code, convert_continent_code_to_continent_name


def valid_doublename(s):
    return re.match("^\w+\.\w+$", s)


def reverse_geocode(lat, lng):
    reverse_data = geocoder.osm_reverse.OsmReverse((lat, lng)).geojson
    country = None
    city = None
    continent = None
    try:
        feature_properties = reverse_data["features"][0]["properties"]
        cc = feature_properties["country_code"].upper()
        city = None
        if "city" in feature_properties:
            city = feature_properties["city"]
        elif "town" in feature_properties:
            city = feature_properties["town"]
        elif "state" in feature_properties:
            city = feature_properties["state"]
        elif "county" in feature_properties:
            city = feature_properties["county"]

        country = pycountry.countries.get(alpha_2=cc).name
        continent_code = country_alpha2_to_continent_code(cc)
        continent = convert_continent_code_to_continent_name(continent_code)
    except:
        return None, None, None
    else:
        return continent, country, city


def get_init_token():
    # get initialization token from user 3bot
    BCDB_NAMESPACE = "threebotuser"

    bcdb = j.tools.open_publish.bcdb_get(BCDB_NAMESPACE, use_zdb=True)
    bcdb.models_add("/sandbox/code/github/threefoldtech/digitalmeX/packages/init_bot/models")

    user_bot_model = bcdb.model_get("threebot.user.initialization")

    user_settings = user_bot_model.get_by_name("user_initialization")
    if not user_settings:
        raise RuntimeError("Initialization token is not set")
    print("user_settings[0].token", user_settings[0].token)
    return user_settings[0].token


def chat(bot):
    """
    to call http://localhost:5050/chat/session/bot_init
    """
    # rndname = j.data.idgenerator.generateXCharID(4)
    clientname = "threebotmain"  # set to rndname in TESTING

    cl = j.clients.tfchain.get(clientname, network_type="TEST")
    cl.save()

    if cl.wallets.count() > 0:
        bot.md_show("Bot has already been initialized and wallet has been configured already")

    real_init_token = get_init_token()

    while True:
        init_token = bot.string_ask("Initialization token").strip()
        if init_token == real_init_token:
            break
        bot.md_show("Invalid initialization token")

    email = bot.string_ask("Enter email", validate={"required": True, "email": True}).strip()

    while True:
        doubleName = bot.string_ask("Double name").strip()
        if valid_doublename(doubleName):
            try:
                # if it's a valid doublename syntactically we should try to check if the doubleName is already reserved.
                cl.threebot.record_get(doubleName)
            except j.clients.tfchain.errors.ThreeBotNotFound:
                print("threebot doublename was found...")
                break
            except Exception as e:
                print(e)
                break
            else:
                bot.md_show("Invalid doubleName {}".format(doubleName))
                continue
            break

    mnemonic = bot.text_ask("Mnemonics? ").strip()
    walletseed = j.data.encryption.mnemonic_to_seed(mnemonic) if mnemonic else ""

    while True:
        location = bot.location_ask("Location? ")
        try:
            lat, lng = [x.strip() for x in location.split(",")]
        except Exception as ex:
            print("ERR: ", ex)
            continue
        else:
            try:
                continent, country, city = reverse_geocode(lat, lng)
            except Exception as ex:
                print("ERR: ", ex)
                continue
            else:
                if continent and country and city:
                    break
    w = cl.wallets.get(clientname, seed=walletseed)
    w.save()
    seed = w.seed

    # dobuleName as name? it should be 5 chars max name no? it's optional nevertheless.
    # <Greenlet at 0x7fa5f49a5748: chat(bot=)> failed with InsufficientFunds
    # TODO: see half baked transactions.

    # res = w.threebot.record_new(months=1, names=[], addresses=[doubleName])

    # ## Should we wait here for transaction acceptance and rollback if not?
    # threebot_transaction = res.transaction
    address = w.address

    R = """
    # You entered

    - email is {{email}}
    - doubleName is {{doubleName}}

    - mnemonic: {{seed}}

    - location {{location}} ->  {{continent}}, {{country}}, {{city}}
    - wallet address: {{address}}

    # Click next

    for the final step which will redirect you to threefold.me

    """
    R2 = j.tools.jinja2.template_render(text=j.core.text.strip(R), **locals())

    bot.md_show(R2)

    # set email on user settings model.

    bot.redirect("https://threefold.me")
