from Jumpscale import j
import os,requests,json

def chat(bot):
    """
    to call http://localhost:8080/session/deploy_website
    """
    res={}
    ip_node = os.environ.get('IP_NODE')
    ip_gateway = os.environ.get('IP_GATEWAY')
    port_gateway = os.environ.get('PORT_GATEWAY')
    webgateway_service_name = os.environ.get('WEBGATEWAY_SERV_NAME')

    # domain_name - which the bot will configure the webgateway to expose
    domain_name = bot.string_ask("Register a domain name then provide the domain name:")
    name = 'web_%s' %domain_name
    repo_url = bot.string_ask("What is the link to the website repo? (using https://github.com/)")
    repo_branch = bot.string_ask("What is the branch to be used in github?")
    jwt = bot.string_ask("What is your JWT token?")
    farm_zerotier_id = bot.string_ask("What is the farm zerotier id?")
    server_type = bot.single_choice("What will the website run on ", ['Caddy', 'ngnix_lapis'])

    # Get zos client instance and create a new container
    zos_node = j.clients.zos.get(name="zos_client_instance", host=ip_node, password=jwt)
    port = zos_node.socat.reserve(1)[0]

    # Create the new container with Caddy or ngnix flist
    if server_type == 'Caddy':
        port_caddy = int(bot.int_ask("What port will Caddy run on?"))
        flist_link = "https://hub.grid.tf/nashaatp/generic_caddy.flist"
        cont_id = zos_node.container.create(flist_link,nics=[{'type':'default','id':'None','hwaddr':'','name':'nat0'},{"name": "zerotier", "type": "zerotier", "id": farm_zerotier_id}],name=name,hostname=name,port={port:port_caddy},tags=[name],env={'REPO_URL':repo_url, 'REPO_BRANCH':repo_branch}).get() # port: {host:container}

    elif server_type == 'ngnix_lapis':
        app_file_location = bot.string_ask("Add path to the application file (Extension .moon) inside the repo ")
        static_location = bot.string_ask("Add path to the static files")
        views_location = bot.string_ask("Add path to the views part of the repo")

        flist_link = "https://hub.grid.tf/tf-autobuilder/threefoldtech-jumpscaleX-autostart-development.flist"
        code_location = '/sandbox/%s' %j.clients.git.parseUrl(repo_url)[3]  
        src1 = code_location+app_file_location
        dest1 = '/sandbox/code/github/threefoldfoundation/lapis-wiki/app.moon'
        src2 = code_location+views_location
        dest2 = '/sandbox/code/github/threefoldfoundation/lapis-wiki/views'
        src3 = code_location+static_location
        dest3 = '/sandbox/code/github/threefoldfoundation/lapis-wiki/static'
        cont_id = zos_node.container.create(flist_link,nics=[{'type':'default','id':'None','hwaddr':'','name':'nat0'},{"name": "zerotier", "type": "zerotier", "id": farm_zerotier_id}],name=name,hostname=name,port={port:8080},tags=[name],env={'REPO_URL':repo_url, 'REPO_BRANCH':repo_branch, 'src1':src1,'dest1':dest1,'src2':src2,'dest2':dest2,'src3':src3,'dest3':dest3}).get() # port: {host:container}

    output = """Website loaded on new container {{cont_id}}"""
    render_output= j.tools.jinja2.template_render(text=j.core.text.strip(output),**locals())
    bot.md_show(render_output)
    
    # Register the website to the webgateway
    create_serv_data = {
        "template": "github.com/threefoldtech/0-templates/reverse_proxy/0.0.1",
        "name": "register_%s" %name,
        "data": {"webGateway": webgateway_service_name,
                "domain": domain_name,
                "servers": ['http://{0}:{1}'.format(ip_node,port)]}
    }
    create_serv_endpoint = "http://{0}:{1}/services".format(ip_gateway,port_gateway)
    req_create_serv = requests.post(create_serv_endpoint, data=json.dumps(create_serv_data) ,headers={'Content-Type': 'application/json'})
    req_json = req_create_serv.status_code

    json_req_create_serv = req_create_serv.json()
    guid = json_req_create_serv['guid']
    secret = json_req_create_serv['secret']
    install_serv_data = {'action_name':'install'}
    install_serv_endpoint = "http://{0}:{1}/services/{2}/task_list".format(ip_gateway,port_gateway,guid)
    install_serv_headers = {
        'Content-Type': 'application/json',
        'ZrobotSecret': 'Bearer %s' %secret
    }
    req_install_serv = requests.post(install_serv_endpoint, data=json.dumps({'action_name':'install'}),headers=install_serv_headers)   

    req_json = req_create_serv.status_code
    R = """Website ready : {{domain_name}}"""
    R2 = j.tools.jinja2.template_render(text=j.core.text.strip(R),**locals())
    bot.md_show(R2)
