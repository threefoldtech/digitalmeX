from Jumpscale import j
import os

def chat(bot):
    """
    to call http://localhost:5050/chat/session/deploy_website
    """
    res={}
    # domain_name - which the bot will configure the webgateway to expose
    domain_name = bot.string_ask("Register a domain name. \n Provide the domain name:")
    name = 'web_%s' %domain_name
    website_repo = bot.string_ask("What is the link to the website repo?")
    jwt = bot.string_ask("What is your JWT token?")
    farm_zerotier_id = bot.string_ask("What is the farm zerotier id?")

    # # parameters of the webgateway info
    # parameters = bot.string_ask("Parameters of the gateway info:")

    app_file_location = bot.string_ask("Add path to the application file (Extension .moon) inside the repo ")
    static_location = bot.string_ask("Add path to the static files")
    views_location = bot.string_ask("Add path to the views part of the repo")
    
    flist_link = "https://hub.grid.tf/tf-autobuilder/threefoldtech-jumpscaleX-autostart-development.flist.md"
    ip_node = os.environ.get('IP_NODE')
    ip_gateway = os.environ.get('IP_GATEWAY')
    port_gateway = os.environ.get('PORT_GATEWAY')
    god_token = os.environ.get('GOD_TOKEN')
    R = """ip:{{ip_gateway}} , port:{{port_gateway}}, token:{{god_token}}"""
    R2 = j.tools.jinja2.template_render(text=j.core.text.strip(R),**locals())
    bot.md_show(R2)

    R = """app:{{app_file_location}} , static:{{static_location}}, views:{{views_location}}"""
    R2 = j.tools.jinja2.template_render(text=j.core.text.strip(R),**locals())
    bot.md_show(R2)

    # Get zos client instance and create a new container
    zos_node = j.clients.zos.get(name="zos_client_instance", host=ip_node, password=jwt)
    
    port = zos_node.socat.reserve(1)[0]
    cont_id = zos_node.container.create(flist_link,nics=[{'type':'default','id':'None','hwaddr':'','name':'nat0'},{"name": "zerotier", "type": "zerotier", "id": farm_zerotier_id}],name=name,hostname=name,port={port:8080},tags=[name]).get() # port: {host:container}

    output = """Port to be used: {{port}}, temp ContainerId: {{cont_id}}"""
    render_output= j.tools.jinja2.template_render(text=j.core.text.strip(output),**locals())
    bot.md_show(render_output)
    cont = zos_node.container.client(cont_id)

    # Deploy website from website_repo on the container created
    code_location = j.clients.git.getContentPathFromURLorPath(website_repo)
    deploy_cmds = """js_shell \"docsite = j.tools.markdowndocs.load({{website_repo}}, name={{domain_name}});docsite.write()\"
    """
    cont.bash(deploy_cmds)
    deploy_cmds_2 = """
    ln -s {{code_location}}/{{app_file_location}} /sandbox/code/github/threefoldfoundation/lapis-wiki/applications
    ln -s {{code_location}}/{{views_location}} /sandbox/code/github/threefoldfoundation/lapis-wiki/views
    ln -s {{code_location}}{{static_location}} /sandbox/code/github/threefoldfoundation/lapis-wiki/static
    js_shell \"j.tools.markdowndocs.webserver()\"
    """
    cont.bash(deploy_cmds_2)
    
    # TODO Register the website to the webgateway


    bot.redirect("https://threefold.me")
